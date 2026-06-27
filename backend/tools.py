import json
import math
import os
import re
from difflib import get_close_matches
from typing import Any, Dict, List, Optional, Tuple

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - fallback when dependency is missing.
    def load_dotenv(*_args, **_kwargs):  # type: ignore[misc]
        return False

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled at runtime if dependency is missing.
    OpenAI = None  # type: ignore[assignment]

# Load env from backend/.env first, then from process environment.
BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API") or os.getenv("OPENAI_API_KEY")

# --- Navigation + Location Knowledge ---

MAP_LOCATIONS = [
    "Main Entrance",
    "Soccer Field",
    "Elementary School",
    "Play Spaces",
    "Cafeteria",
    "Lower Hill",
    "Middle School",
    "Secondary Library",
    "Performing Arts",
    "High School",
    "Outdoor Field",
    "G Building",
    "Bus Area",
]

LOCATION_DETAILS = {
    "Main Entrance": "Primary visitor and student entry point for the campus.",
    "Soccer Field": "Main pitch used for PE classes, soccer practice, and games.",
    "Elementary School": "Building area with elementary classrooms, including A-series rooms.",
    "Play Spaces": "Outdoor recreation zone connected between elementary and middle areas.",
    "Cafeteria": "Central dining area and walking hub for multiple routes.",
    "Lower Hill": "Sloped connector path between central campus and performing arts side.",
    "Middle School": "Middle school academic building with M-series classrooms.",
    "Secondary Library": "Secondary library and study space with research and seminar rooms.",
    "Performing Arts": "Music, drama, and rehearsal area for performances and arts programs.",
    "High School": "High school academic area with H-series classrooms.",
    "Outdoor Field": "Multi-use field for athletics, PE, and outdoor activities.",
    "G Building": "Academic building for specialized classes and G-series classrooms.",
    "Bus Area": "Transportation pickup and drop-off point.",
}

# Classroom and alias mapping for destination resolution.
CLASSROOM_TO_LOCATION = {
    "A101": "Elementary School",
    "A102": "Elementary School",
    "A201": "Elementary School",
    "A203": "Elementary School",
    "M101": "Middle School",
    "M202": "Middle School",
    "M305": "Middle School",
    "H101": "High School",
    "H203": "High School",
    "H305": "High School",
    "G101": "G Building",
    "G102": "G Building",
    "G201": "G Building",
    "LIB201": "Secondary Library",
    "LIB202": "Secondary Library",
}

MANUAL_LOCATION_ALIASES = {
    "entrance": "Main Entrance",
    "front gate": "Main Entrance",
    "main gate": "Main Entrance",
    "soccer": "Soccer Field",
    "soccer pitch": "Soccer Field",
    "elementary": "Elementary School",
    "a building": "Elementary School",
    "playground": "Play Spaces",
    "play area": "Play Spaces",
    "lunch room": "Cafeteria",
    "dining hall": "Cafeteria",
    "lower slope": "Lower Hill",
    "middle": "Middle School",
    "library": "Secondary Library",
    "secondary lib": "Secondary Library",
    "arts": "Performing Arts",
    "performing arts center": "Performing Arts",
    "high": "High School",
    "outdoor": "Outdoor Field",
    "field": "Outdoor Field",
    "building g": "G Building",
    "bus": "Bus Area",
    "bus stop": "Bus Area",
}

# --- Customizable RAG Data ---

# Main editable knowledge file (plain text, separated by blank lines).
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "school_knowledge.txt")
# Optional structured extension file (list of strings or dict entries).
CUSTOM_KNOWLEDGE_FILE = os.path.join(BASE_DIR, "school_knowledge_custom.json")

_EMBEDDING_MODEL = "text-embedding-3-small"

_client: Optional[Any] = None
_cached_signature: Optional[Tuple[Optional[float], Optional[float]]] = None
_cached_chunks: List[str] = []
_cached_embeddings: List[List[float]] = []


def _get_client() -> Optional[Any]:
    global _client
    if _client is not None:
        return _client
    if not OPENAI_API_KEY or OpenAI is None:
        return None
    _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def has_openai_client() -> bool:
    return _get_client() is not None


def get_openai_client() -> Optional[Any]:
    return _get_client()


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def _compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _build_alias_map() -> Dict[str, str]:
    alias_to_location: Dict[str, str] = {}

    for location in MAP_LOCATIONS:
        alias_to_location[_normalize(location)] = location

    for alias, location in MANUAL_LOCATION_ALIASES.items():
        alias_to_location[_normalize(alias)] = location

    for classroom, location in CLASSROOM_TO_LOCATION.items():
        normalized = _normalize(classroom)
        compact = _compact(classroom)
        alias_to_location[normalized] = location
        alias_to_location[compact] = location

    return alias_to_location


ALIAS_TO_LOCATION = _build_alias_map()


def get_location_description(location: str) -> str:
    nav_result = navigate_to_location(location)
    if not nav_result.get("success"):
        return "No description available for this location."
    canonical = nav_result["location"]
    return LOCATION_DETAILS.get(canonical, "No description available for this location.")


def _extract_classroom_candidates(text: str) -> List[str]:
    raw_tokens = re.findall(r"[A-Za-z]{1,4}\s*-?\d{2,3}", text)
    compact_tokens = [_compact(token) for token in raw_tokens]
    return [token for token in compact_tokens if token]


def navigate_to_location(location: str):
    """Resolve user-provided place/classroom text to a map location."""
    if not location:
        return {"success": False, "error": "No location provided."}

    cleaned = _normalize(location)
    compact = _compact(location)

    if cleaned in ALIAS_TO_LOCATION:
        canonical = ALIAS_TO_LOCATION[cleaned]
        return {
            "success": True,
            "location": canonical,
            "description": LOCATION_DETAILS.get(canonical, ""),
        }

    if compact in ALIAS_TO_LOCATION:
        canonical = ALIAS_TO_LOCATION[compact]
        return {
            "success": True,
            "location": canonical,
            "description": LOCATION_DETAILS.get(canonical, ""),
        }

    best_substring_match: Optional[Tuple[int, str]] = None
    for alias, canonical in ALIAS_TO_LOCATION.items():
        if not alias:
            continue
        if alias in cleaned:
            alias_length = len(alias)
            if best_substring_match is None or alias_length > best_substring_match[0]:
                best_substring_match = (alias_length, canonical)

    if best_substring_match is not None:
        canonical = best_substring_match[1]
        return {
            "success": True,
            "location": canonical,
            "description": LOCATION_DETAILS.get(canonical, ""),
        }

    classroom_tokens = _extract_classroom_candidates(location)
    for token in classroom_tokens:
        if token in ALIAS_TO_LOCATION:
            canonical = ALIAS_TO_LOCATION[token]
            return {
                "success": True,
                "location": canonical,
                "description": LOCATION_DETAILS.get(canonical, ""),
            }

    closest = get_close_matches(cleaned, list(ALIAS_TO_LOCATION.keys()), n=1, cutoff=0.82)
    if closest:
        canonical = ALIAS_TO_LOCATION[closest[0]]
        return {
            "success": True,
            "location": canonical,
            "description": LOCATION_DETAILS.get(canonical, ""),
        }

    return {
        "success": False,
        "error": (
            f"Location '{location}' not found. Available map destinations: "
            f"{', '.join(MAP_LOCATIONS)}"
        ),
    }


def resolve_navigation_route(start: str, destination: str) -> Dict[str, Any]:
    """Resolve both ends of a navigation request into canonical map locations."""
    start_result = navigate_to_location(start)
    if not start_result.get("success"):
        return {
            "success": False,
            "error": f"Could not resolve the starting location '{start}'.",
            "details": start_result,
        }

    destination_result = navigate_to_location(destination)
    if not destination_result.get("success"):
        return {
            "success": False,
            "error": f"Could not resolve the destination '{destination}'.",
            "details": destination_result,
        }

    canonical_start = start_result["location"]
    canonical_destination = destination_result["location"]

    if canonical_start == canonical_destination:
        return {
            "success": False,
            "error": "Start and destination resolve to the same map location.",
            "start": canonical_start,
            "destination": canonical_destination,
        }

    return {
        "success": True,
        "start": canonical_start,
        "destination": canonical_destination,
        "start_description": LOCATION_DETAILS.get(canonical_start, ""),
        "destination_description": LOCATION_DETAILS.get(canonical_destination, ""),
    }


def get_available_locations() -> List[str]:
    return list(MAP_LOCATIONS)


def _get_file_mtime(path: str) -> Optional[float]:
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def _current_signature() -> Tuple[Optional[float], Optional[float]]:
    return (_get_file_mtime(KNOWLEDGE_FILE), _get_file_mtime(CUSTOM_KNOWLEDGE_FILE))


def _load_text_chunks(path: str) -> List[str]:
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    return [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]


def _load_custom_chunks(path: str) -> List[str]:
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    chunks: List[str] = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, str) and item.strip():
                chunks.append(item.strip())
                continue

            if not isinstance(item, dict):
                continue

            title = str(item.get("title", "")).strip()
            content = str(item.get("content", "")).strip()
            tags = item.get("tags", [])

            tag_text = ""
            if isinstance(tags, list) and tags:
                safe_tags = [str(tag).strip() for tag in tags if str(tag).strip()]
                if safe_tags:
                    tag_text = f"Tags: {', '.join(safe_tags)}"

            block_parts = [part for part in [title, content, tag_text] if part]
            if block_parts:
                chunks.append("\n".join(block_parts))

    return chunks


def _refresh_chunks_if_needed(force_refresh: bool = False) -> None:
    global _cached_signature
    global _cached_chunks
    global _cached_embeddings

    signature = _current_signature()
    if not force_refresh and signature == _cached_signature and _cached_chunks:
        return

    text_chunks = _load_text_chunks(KNOWLEDGE_FILE)
    custom_chunks = _load_custom_chunks(CUSTOM_KNOWLEDGE_FILE)

    fallback_chunks = [
        f"{location}: {LOCATION_DETAILS[location]}" for location in MAP_LOCATIONS
    ]

    deduped_chunks: List[str] = []
    seen = set()
    for chunk in text_chunks + custom_chunks + fallback_chunks:
        normalized_chunk = _normalize(chunk)
        if not normalized_chunk or normalized_chunk in seen:
            continue
        seen.add(normalized_chunk)
        deduped_chunks.append(chunk)

    _cached_signature = signature
    _cached_chunks = deduped_chunks
    _cached_embeddings = []


def _batch(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _compute_embeddings(chunks: List[str]) -> List[List[float]]:
    client = _get_client()
    if client is None or not chunks:
        return []

    embeddings: List[List[float]] = []
    try:
        for batch in _batch(chunks, 64):
            response = client.embeddings.create(model=_EMBEDDING_MODEL, input=batch)
            ordered = sorted(response.data, key=lambda row: row.index)
            embeddings.extend([row.embedding for row in ordered])
    except Exception:
        return []

    return embeddings


def _ensure_embeddings(force_refresh: bool = False) -> None:
    global _cached_embeddings

    _refresh_chunks_if_needed(force_refresh=force_refresh)

    if _cached_embeddings and len(_cached_embeddings) == len(_cached_chunks):
        return

    _cached_embeddings = _compute_embeddings(_cached_chunks)


def refresh_knowledge_cache() -> int:
    """Force reload of knowledge files so updates are picked up immediately."""
    _ensure_embeddings(force_refresh=True)
    return len(_cached_chunks)


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0

    for x, y in zip(a, b):
        dot += x * y
        norm_a += x * x
        norm_b += y * y

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


def _keyword_score(query: str, chunk: str) -> float:
    q_terms = set(re.findall(r"[a-z0-9]+", _normalize(query)))
    c_terms = set(re.findall(r"[a-z0-9]+", _normalize(chunk)))

    if not q_terms or not c_terms:
        return 0.0

    overlap = len(q_terms & c_terms)
    if overlap == 0:
        return 0.0

    ratio = overlap / math.sqrt(len(q_terms) * len(c_terms))
    phrase_bonus = 0.15 if _normalize(query) in _normalize(chunk) else 0.0
    return ratio + phrase_bonus


def search_school_database(query: str, top_k: int = 4) -> List[str]:
    """Semantic retrieval over school knowledge. Edit knowledge files anytime."""
    if not query.strip():
        return []

    _ensure_embeddings(force_refresh=False)

    if not _cached_chunks:
        return []

    client = _get_client()

    scored_results: List[Tuple[float, str]] = []

    if client is not None and _cached_embeddings and len(_cached_embeddings) == len(_cached_chunks):
        try:
            query_embedding = client.embeddings.create(
                model=_EMBEDDING_MODEL,
                input=[query],
            ).data[0].embedding

            for chunk, embedding in zip(_cached_chunks, _cached_embeddings):
                score = _cosine_similarity(query_embedding, embedding)
                scored_results.append((score, chunk))
        except Exception:
            scored_results = []

    if not scored_results:
        for chunk in _cached_chunks:
            score = _keyword_score(query, chunk)
            scored_results.append((score, chunk))

    scored_results.sort(key=lambda row: row[0], reverse=True)

    top_chunks = [chunk for score, chunk in scored_results if score > 0][:top_k]
    if not top_chunks:
        top_chunks = [chunk for _, chunk in scored_results[:top_k]]

    return top_chunks
