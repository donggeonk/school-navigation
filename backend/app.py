from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from models import SchoolMap
import os

app = Flask(__name__)
CORS(app)

school_map = SchoolMap()

# Path to frontend files
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src')

@app.route('/')
def serve_index():
    """Serve the main HTML page"""
    return send_from_directory(FRONTEND_PATH, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS)"""
    return send_from_directory(FRONTEND_PATH, filename)

@app.route('/api/map', methods=['GET'])
def get_map():
    """Return all nodes and their coordinates"""
    nodes_data = []
    for name, node in school_map.nodes.items():
        nodes_data.append({
            'name': name,
            'coordinates': node.coordinates,
            'connections': [conn.name for conn in node.connections]
        })
    return jsonify(nodes_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)