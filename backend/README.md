# School Navigation App Backend

This is the backend component of the School Navigation App, which provides navigation services for the school campus.

## Overview

The backend is built using Python and Flask, serving as the API for the frontend application. It handles requests related to navigation between various locations on the school campus, including buildings, fields, and parking lots.

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd school-navigation-app/backend
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```
   python app.py
   ```

The backend will start running on `http://localhost:5000`.

## API Endpoints

- **GET /api/navigate**: Computes the navigation path between two locations.
- **GET /api/map**: Returns all map nodes and their coordinates.
- **POST /api/chat**: Chatbot endpoint powered by OpenAI + local RAG context.

## Chatbot Setup

1. Add your OpenAI key to `backend/.env`:
   ```
   OPENAI_API="your-openai-api-key"
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Customize RAG data anytime:
   - `backend/school_knowledge.txt` for plain-text chunks (separate topics with blank lines)
   - `backend/school_knowledge_custom.json` for structured entries (`title`, `content`, `tags`)

The chatbot auto-reloads these files and uses them for retrieval.

## Future Plans

- Add detailed classroom information and floor blueprints.
- Implement user authentication for personalized navigation experiences.
- Enhance the navigation algorithm to consider accessibility options.