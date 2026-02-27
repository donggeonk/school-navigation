import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from models import SchoolMap

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

school_map = SchoolMap()

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/api/map')
def get_map():
    nodes = []
    for name, node in school_map.nodes.items():
        nodes.append({
            'name': name,
            'coordinates': list(node.coordinates),
            'connections': [c.name for c in node.connections]
        })
    return jsonify(nodes)

@app.route('/api/navigate')
def navigate():
    start = request.args.get('start')
    end = request.args.get('end')

    if not start or not end:
        return jsonify({'error': 'Missing start or end parameter'}), 400

    path = school_map.find_shortest_path(start, end)

    if path is None:
        return jsonify({'error': 'No path found'}), 404

    return jsonify({
        'start': start,
        'end': end,
        'path': path  # List of [x, y] coordinates
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)