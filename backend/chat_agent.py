import json
import re
from typing import Any, Dict, List, Optional

from tools import (
    get_available_locations,
    get_openai_client,
    has_openai_client,
    navigate_to_location,
    resolve_navigation_route,
    search_school_database,
)

MODEL_NAME = "gpt-4o-mini"

BLUEPRINT_FLOORS = {
    "High School": ["B", "1", "2", "3", "4", "5", "6", "7"],
    "Middle School": ["1"],
    "Elementary School": ["1", "2"],
    "Cafeteria": ["1", "2", "2-1"],
}

BLUEPRINT_BUILDING_ALIASES = {
    "high school": "High School",
    "high_school": "High School",
    "hs": "High School",
    "middle school": "Middle School",
    "middle_school": "Middle School",
    "ms": "Middle School",
    "elementary school": "Elementary School",
    "elementary_school": "Elementary School",
    "elementary": "Elementary School",
    "es": "Elementary School",
    "cafeteria": "Cafeteria",
    "cafe": "Cafeteria",
    "dining hall": "Cafeteria",
}

FLOOR_WORDS = {
    "first": "1",
    "one": "1",
    "second": "2",
    "two": "2",
    "third": "3",
    "three": "3",
    "fourth": "4",
    "four": "4",
    "fifth": "5",
    "five": "5",
    "sixth": "6",
    "six": "6",
    "seventh": "7",
    "seven": "7",
}


def _tool_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "search_school_database",
                "description": (
                    "Retrieve top school knowledge snippets for questions about buildings, "
                    "classrooms, events, and campus information."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "User question rewritten as a focused retrieval query.",
                        }
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "navigate_to_location",
                "description": (
                    "Resolve classroom/building/place text to a map destination on campus. "
                    "Use when user asks where a room is or asks to go somewhere."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Destination text from user (e.g., A101, G Building, Soccer Field).",
                        }
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "resolve_navigation_route",
                "description": (
                    "Resolve a route request into canonical start and destination map locations. "
                    "Use this when the user asks for directions between two places."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "string",
                            "description": "Starting location text from the user or current map context.",
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination text from the user.",
                        },
                    },
                    "required": ["start", "destination"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "open_building_blueprint",
                "description": (
                    "Open a building blueprint popup in the map app. Use when the user asks "
                    "to see a building blueprint, floor plan, layout, basement, or a specific floor."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "building": {
                            "type": "string",
                            "description": (
                                "Building name or alias. Supported buildings: High School, "
                                "Middle School, Elementary School, Cafeteria."
                            ),
                        },
                        "floor": {
                            "type": "string",
                            "description": (
                                "Optional requested floor. Examples: 1, 2, 2-1, B, base, basement, first."
                            ),
                        },
                    },
                    "required": ["building"],
                },
            },
        },
    ]


def _build_system_prompt(current_start: str = "", current_destination: str = "") -> str:
    locations = ", ".join(get_available_locations())

    current_context = ""
    if current_start or current_destination:
        current_context = (
            f"Current navigation selections -> start: '{current_start or 'none'}', "
            f"destination: '{current_destination or 'none'}'."
        )

    return f"""You are the KIS campus assistant for a school map web app.

Your goals:
1) Help users find where classrooms/buildings are.
2) Answer questions using retrieved school knowledge snippets.
3) If the user asks to go somewhere, resolve a valid map destination.

Available map destinations: {locations}
{current_context}

Rules:
- Use search_school_database for building/classroom/event information.
- Use navigate_to_location when the user asks where something is or wants navigation.
- Use resolve_navigation_route when the user asks for directions between two places.
- Use open_building_blueprint when the user asks to see a building blueprint, floor plan, layout, basement, or specific floor.
- If the user asks to go somewhere and a current start is already selected, you may use that current start.
- If the user asks for a building blueprint without a floor, open the first floor.
- If a classroom is requested, identify the building and mention it clearly.
- Keep responses concise and practical.
- If event details are uncertain, state that schedules can change and suggest checking announcements.
"""


def _get_openai_client() -> Optional[Any]:
    if not has_openai_client():
        return None

    return get_openai_client()


def _safe_json_loads(raw: str) -> Dict[str, Any]:
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return {}


def _blueprint_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("_", " ")).strip()


def _resolve_blueprint_building(text: str) -> Optional[str]:
    normalized = _blueprint_text(text)

    for alias, building in sorted(
        BLUEPRINT_BUILDING_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        alias_text = _blueprint_text(alias)
        if re.search(rf"(?<![a-z0-9]){re.escape(alias_text)}(?![a-z0-9])", normalized):
            return building

    return None


def _has_blueprint_intent(text: str) -> bool:
    normalized = _blueprint_text(text)
    direct_terms = [
        "blueprint",
        "floor plan",
        "floorplan",
        "layout",
    ]
    if any(term in normalized for term in direct_terms):
        return True

    action_terms = ["show", "open", "see", "view", "display", "pull up"]
    floor_terms = ["floor", "level", "basement", "base"]
    return (
        any(term in normalized for term in action_terms)
        and any(term in normalized for term in floor_terms)
    )


def _floor_display_name(label: str) -> str:
    if label == "B":
        return "basement"
    if label == "1":
        return "first floor"
    return f"floor {label}"


def _normalize_requested_floor(floor_text: str) -> Optional[str]:
    if not floor_text:
        return None

    raw = floor_text.lower().strip()
    normalized = _blueprint_text(raw)

    if re.search(r"\b(base|basement)\b", normalized):
        return "B"

    for word, label in FLOOR_WORDS.items():
        if re.search(rf"\b{word}\b", normalized):
            return label

    compound_match = re.search(r"\b(\d+)\s*[-_]\s*(\d+)\b", raw)
    if compound_match:
        return f"{compound_match.group(1)}-{compound_match.group(2)}"

    digit_match = re.search(r"\b(\d+)(?:st|nd|rd|th)?\b", normalized)
    if digit_match:
        return digit_match.group(1)

    return None


def _extract_requested_floor(text: str) -> Optional[str]:
    raw = text.lower()
    normalized = _blueprint_text(text)

    if re.search(r"\b(base|basement)\b", normalized):
        return "B"

    compound_match = re.search(r"\b(\d+)\s*[-_]\s*(\d+)\b", raw)
    if compound_match:
        return f"{compound_match.group(1)}-{compound_match.group(2)}"

    floor_patterns = [
        r"\b(?:floor|level)\s+(\d+)(?:st|nd|rd|th)?\b",
        r"\b(\d+)(?:st|nd|rd|th)?\s+(?:floor|level)\b",
    ]
    for pattern in floor_patterns:
        match = re.search(pattern, normalized)
        if match:
            return match.group(1)

    for word, label in FLOOR_WORDS.items():
        if re.search(rf"\b{word}\s+(?:floor|level)\b", normalized):
            return label
        if re.search(rf"\b(?:floor|level)\s+{word}\b", normalized):
            return label

    building = _resolve_blueprint_building(text)
    if building and _has_blueprint_intent(text):
        available = set(BLUEPRINT_FLOORS[building])
        for label in available:
            if label == "B":
                continue
            if re.search(rf"\b{re.escape(label)}(?:st|nd|rd|th)?\b", normalized):
                return label

    return None


def _build_blueprint_payload(building: str, requested_floor: Optional[str] = None) -> Dict[str, Any]:
    available_floors = BLUEPRINT_FLOORS[building]
    floor = requested_floor or "1"
    floor_was_available = floor in available_floors

    if not floor_was_available:
        floor = "1"

    return {
        "building": building,
        "floor": floor,
        "requested_floor": requested_floor or floor,
        "available_floors": available_floors,
        "floor_was_available": floor_was_available,
    }


def resolve_blueprint_request(building_text: str, floor_text: str = "") -> Dict[str, Any]:
    building = _resolve_blueprint_building(building_text)
    if building is None:
        return {
            "success": False,
            "error": (
                "I can open blueprints for High School, Middle School, "
                "Elementary School, and Cafeteria."
            ),
        }

    requested_floor = _normalize_requested_floor(floor_text) if floor_text else None
    payload = _build_blueprint_payload(building, requested_floor)
    return {
        "success": True,
        **payload,
    }


def _heuristic_blueprint_payload(user_input: str) -> Optional[Dict[str, Any]]:
    building = _resolve_blueprint_building(user_input)
    if building is None or not _has_blueprint_intent(user_input):
        return None

    requested_floor = _extract_requested_floor(user_input)
    return _build_blueprint_payload(building, requested_floor)


def _blueprint_message(blueprint: Dict[str, Any]) -> str:
    floor = blueprint["floor"]
    building = blueprint["building"]
    requested_floor = blueprint.get("requested_floor")

    if requested_floor and requested_floor != floor:
        available = ", ".join(blueprint.get("available_floors", []))
        return (
            f"I do not have {building} {_floor_display_name(requested_floor)}. "
            f"Showing the first floor blueprint instead. Available floors: {available}."
        )

    return f"Showing the {building} {_floor_display_name(floor)} blueprint."


def _tool_response_for(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "search_school_database":
        query = str(arguments.get("query", "")).strip()
        return {"results": search_school_database(query)}

    if name == "navigate_to_location":
        location = str(arguments.get("location", "")).strip()
        return navigate_to_location(location)

    if name == "resolve_navigation_route":
        start = str(arguments.get("start", "")).strip()
        destination = str(arguments.get("destination", "")).strip()
        return resolve_navigation_route(start, destination)

    if name == "open_building_blueprint":
        building = str(arguments.get("building", "")).strip()
        floor = str(arguments.get("floor", "")).strip()
        return resolve_blueprint_request(building, floor)

    return {"error": f"Unknown tool: {name}"}


def _payload_with_blueprint(blueprint: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "message": _blueprint_message(blueprint),
        "blueprint": {
            "building": blueprint["building"],
            "floor": blueprint["floor"],
        },
    }


def _looks_like_navigation_request(user_input: str) -> bool:
    lowered = user_input.lower()
    navigation_phrases = [
        "go to",
        "take me to",
        "navigate",
        "how do i get",
        "where is",
        "way to",
        "route to",
    ]
    return any(phrase in lowered for phrase in navigation_phrases)


def _looks_like_route_execution_request(user_input: str) -> bool:
    lowered = user_input.lower()
    route_phrases = [
        "go to",
        "take me to",
        "navigate",
        "how do i get",
        "way to",
        "route to",
    ]
    return any(phrase in lowered for phrase in route_phrases)


def _clean_route_fragment(fragment: str) -> str:
    cleaned = fragment.strip().strip(".,!?;:")
    cleaned = re.sub(r"\bplease\b", "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned


def _extract_route_segments(user_input: str) -> Optional[Dict[str, str]]:
    patterns = [
        r"\bfrom\s+(?P<start>.+?)\s+to\s+(?P<destination>.+?)(?:[.?!]|$)",
        r"\bto\s+(?P<destination>.+?)\s+from\s+(?P<start>.+?)(?:[.?!]|$)",
        r"\bbetween\s+(?P<start>.+?)\s+and\s+(?P<destination>.+?)(?:[.?!]|$)",
        r"\bat\s+(?P<start>.+?)\s+and\s+(?:need|want|would like).+?\bto\s+(?P<destination>.+?)(?:[.?!]|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, user_input, flags=re.IGNORECASE)
        if not match:
            continue

        start = _clean_route_fragment(match.group("start"))
        destination = _clean_route_fragment(match.group("destination"))
        if start and destination:
            return {"start": start, "destination": destination}

    return None


def _heuristic_navigation_payload(
    user_input: str,
    current_start: str = "",
) -> Optional[Dict[str, Any]]:
    route_segments = _extract_route_segments(user_input)
    if route_segments:
        route = resolve_navigation_route(
            route_segments["start"],
            route_segments["destination"],
        )
        if route.get("success"):
            return route
        return None

    if current_start and _looks_like_route_execution_request(user_input):
        destination_result = navigate_to_location(user_input)
        if destination_result.get("success"):
            route = resolve_navigation_route(current_start, destination_result["location"])
            if route.get("success"):
                return route

    return None


def _fallback_without_llm(user_input: str, current_start: str = "") -> Dict[str, Any]:
    blueprint = _heuristic_blueprint_payload(user_input)
    if blueprint:
        return _payload_with_blueprint(blueprint)

    route = _heuristic_navigation_payload(user_input, current_start=current_start)
    if route:
        return {
            "message": (
                f"Showing the route from {route['start']} to {route['destination']}."
            ),
            "navigation": {
                "start": route["start"],
                "destination": route["destination"],
            },
            "suggested_destination": route["destination"],
        }

    snippets = search_school_database(user_input)
    nav = navigate_to_location(user_input)

    if _looks_like_navigation_request(user_input) and nav.get("success"):
        return {
            "message": (
                f"{nav['location']} is the best map match. "
                f"{nav.get('description', '')}".strip()
            ),
            "suggested_destination": nav["location"],
        }

    if snippets:
        return {
            "message": snippets[0],
            "sources": snippets,
        }

    if nav.get("success"):
        return {
            "message": (
                f"{nav['location']} is the best map match. "
                f"{nav.get('description', '')}".strip()
            ),
            "suggested_destination": nav["location"],
        }

    return {
        "message": (
            "I could not find enough information. Add details to backend/school_knowledge.txt "
            "or backend/school_knowledge_custom.json and try again."
        )
    }


def school_chat(user_input: str, current_start: str = "", current_destination: str = "") -> Dict[str, Any]:
    """Main chatbot entrypoint used by Flask /api/chat."""
    user_input = (user_input or "").strip()
    if not user_input:
        return {"message": "Please type a question first."}

    heuristic_blueprint = _heuristic_blueprint_payload(user_input)
    if heuristic_blueprint:
        return _payload_with_blueprint(heuristic_blueprint)

    heuristic_navigation = _heuristic_navigation_payload(
        user_input,
        current_start=current_start,
    )

    client = _get_openai_client()
    if client is None:
        fallback = _fallback_without_llm(user_input, current_start=current_start)
        fallback["message"] += (
            " (OpenAI is not fully configured: install `openai` and set OPENAI_API in backend/.env "
            "for full chatbot mode.)"
        )
        return fallback

    tools = _tool_schemas()

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": _build_system_prompt(current_start, current_destination)},
        {"role": "user", "content": user_input},
    ]

    try:
        first_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
        )
    except Exception:
        fallback = _fallback_without_llm(user_input, current_start=current_start)
        fallback["message"] += " (OpenAI request failed, so I used local school data instead.)"
        return fallback

    first_message = first_response.choices[0].message
    tool_calls = first_message.tool_calls or []

    if not tool_calls:
        return {"message": first_message.content or "I could not generate a response."}

    assistant_tool_message = {
        "role": "assistant",
        "content": first_message.content or "",
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }
            for call in tool_calls
        ],
    }

    tool_messages: List[Dict[str, Any]] = []
    suggested_destination: Optional[str] = None
    navigation: Optional[Dict[str, str]] = None
    blueprint: Optional[Dict[str, Any]] = None

    for call in tool_calls:
        function_name = call.function.name
        arguments = _safe_json_loads(call.function.arguments)
        result = _tool_response_for(function_name, arguments)

        if function_name == "navigate_to_location" and result.get("success"):
            suggested_destination = result.get("location")
        if function_name == "resolve_navigation_route" and result.get("success"):
            navigation = {
                "start": result["start"],
                "destination": result["destination"],
            }
            suggested_destination = result["destination"]
        if function_name == "open_building_blueprint" and result.get("success"):
            blueprint = {
                "building": result["building"],
                "floor": result["floor"],
                "requested_floor": result.get("requested_floor"),
                "available_floors": result.get("available_floors", []),
            }

        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "name": function_name,
                "content": json.dumps(result),
            }
        )

    final_messages = messages + [assistant_tool_message] + tool_messages

    try:
        followup = client.chat.completions.create(
            model=MODEL_NAME,
            messages=final_messages,
            temperature=0.2,
        )
    except Exception:
        fallback = _fallback_without_llm(user_input, current_start=current_start)
        if navigation and "navigation" not in fallback:
            fallback["navigation"] = navigation
            fallback["suggested_destination"] = navigation["destination"]
        fallback["message"] += " (OpenAI request failed, so I used local school data instead.)"
        return fallback

    payload: Dict[str, Any] = {
        "message": followup.choices[0].message.content or "I could not generate a final response.",
    }

    if suggested_destination:
        payload["suggested_destination"] = suggested_destination

    if navigation:
        payload["navigation"] = navigation
    elif heuristic_navigation:
        payload["navigation"] = {
            "start": heuristic_navigation["start"],
            "destination": heuristic_navigation["destination"],
        }
        payload["suggested_destination"] = heuristic_navigation["destination"]

    if blueprint:
        payload["blueprint"] = {
            "building": blueprint["building"],
            "floor": blueprint["floor"],
        }

    return payload
