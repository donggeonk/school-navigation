# School Navigation App

This project is a web application designed to provide navigation assistance within a school campus. It features a static overview of the campus map, including three buildings, one field, and one parking lot. Users can input their starting location and desired destination to receive navigation paths.

## Project Structure

The project is divided into two main components: the frontend and the backend.

### Frontend

The frontend is built using HTML, CSS, and JavaScript. It includes the following files:

- **index.html**: The main HTML page that sets up the structure of the application.
- **index.js**: The entry point for the frontend JavaScript, managing user input and rendering the map.
- **styles.css**: Contains the CSS styles for the application.
- **components/**: A directory containing modular components:
  - **map.js**: Handles the rendering of the static map overview and navigation lines.
  - **search.js**: Manages input boxes for start and destination locations.
  - **navigation.js**: Computes the navigation path between nodes.

### Backend

The backend is implemented in Python using Flask. It includes the following files:

- **app.py**: The main entry point for the backend application.
- **routes.py**: Defines the API routes for navigation and other features.
- **models.py**: Contains data models representing the school map and connections.
- **utils.py**: Includes utility functions for path computation.
- **requirements.txt**: Lists the Python dependencies required for the backend.

## Setup Instructions

### Frontend

1. Navigate to the `frontend` directory.
2. Install the necessary dependencies using npm:
   ```
   npm install
   ```
3. Start the frontend development server:
   ```
   npm start
   ```

### Backend

1. Navigate to the `backend` directory.
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the backend application:
   ```
   python app.py
   ```

## Future Plans

- Add detailed classroom information and floor blueprints.
- Implement accessibility features for navigation.
- Enhance the navigation algorithm for better pathfinding.

## Contributions

Contributions to improve the project are welcome. Please feel free to submit issues or pull requests.