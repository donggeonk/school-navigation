from flask import Flask, request, jsonify
from models import Node, Graph
from utils import calculate_path

app = Flask(__name__)

# Sample data for the school map
nodes = {
    "Building A": Node("Building A", (1, 2)),
    "Building B": Node("Building B", (3, 4)),
    "Building C": Node("Building C", (5, 6)),
    "Field": Node("Field", (2, 3)),
    "Parking Lot": Node("Parking Lot", (4, 1)),
}

# Define connections between nodes
connections = {
    "Building A": ["Field", "Building B"],
    "Building B": ["Building A", "Building C"],
    "Building C": ["Building B", "Parking Lot"],
    "Field": ["Building A"],
    "Parking Lot": ["Building C"],
}

graph = Graph(nodes, connections)

@app.route('/api/navigate', methods=['POST'])
def navigate():
    data = request.json
    start = data.get('start')
    destination = data.get('destination')

    if start not in nodes or destination not in nodes:
        return jsonify({"error": "Invalid start or destination"}), 400

    path = calculate_path(graph, start, destination)
    return jsonify({"path": path})

if __name__ == '__main__':
    app.run(debug=True)