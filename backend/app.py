import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from models import SchoolMap
from chat_agent import school_chat

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

school_map = SchoolMap()

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

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


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    current_start = (data.get('start') or '').strip()
    current_destination = (data.get('destination') or '').strip()

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        response = school_chat(
            message,
            current_start=current_start,
            current_destination=current_destination
        )
    except Exception as exc:
        return jsonify({'error': f'Chat request failed: {exc}'}), 500

    return jsonify(response)


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
