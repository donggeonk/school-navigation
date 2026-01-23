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
- **GET /api/locations**: Returns the list of available locations on the campus.

## Future Plans

- Add detailed classroom information and floor blueprints.
- Implement user authentication for personalized navigation experiences.
- Enhance the navigation algorithm to consider accessibility options.

## Contributions

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.