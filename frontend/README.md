# Frontend Navigation App

This is the frontend part of the School Navigation App, which provides a user-friendly interface for navigating the school premises.

## Project Structure

- **src/index.html**: The main HTML page that sets up the structure of the application.
- **src/index.js**: The entry point for the frontend JavaScript, handling user input and rendering.
- **src/styles.css**: Contains the CSS styles for the application.
- **src/components/map.js**: Renders the static map overview and navigation lines.
- **src/components/search.js**: Manages input boxes for start and destination locations.
- **src/components/navigation.js**: Computes the navigation path between nodes.

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd school-navigation-app/frontend
   ```

2. **Install dependencies**:
   ```
   npm install
   ```

3. **Run the application**:
   ```
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000` to view the application.

## Usage Guidelines

- Enter the start and destination locations in the provided input boxes.
- Click the search button to visualize the navigation path on the map.
- Ensure that the map is properly rendered with all buildings, the field, and the parking lot.

## Future Plans

- Integrate classroom details and floor blueprints for more detailed navigation.
- Enhance accessibility features to support all users.

For any issues or contributions, please refer to the main project repository.