from flask import Flask, jsonify, request, send_from_directory, abort
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='web')
BASE = os.path.dirname(__file__)
AGENDA_FILE = os.path.join(BASE, 'agenda.json')


def load_agenda():
    if os.path.exists(AGENDA_FILE):
        try:
            with open(AGENDA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_agenda(data):
    with open(AGENDA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:fp>')
def static_files(fp):
    return send_from_directory(app.static_folder, fp)


@app.route('/api/agenda', methods=['GET'])
def api_get_agenda():
    return jsonify(load_agenda())


@app.route('/api/agenda', methods=['POST'])
def api_add():
    data = request.get_json()
    if not data:
        abort(400)
    agenda = load_agenda()
    new_id = int(datetime.now().timestamp() * 1000)
    note = {
        'id': new_id,
        'text': data.get('text', ''),
        'datetime': data.get('datetime'),
        'triggered': False,
        'repeat': data.get('repeat', 'None'),
        'completed': False
    }
    agenda.append(note)
    save_agenda(agenda)
    return jsonify(note), 201


@app.route('/api/agenda/<int:note_id>', methods=['DELETE'])
def api_delete(note_id):
    agenda = load_agenda()
    new = [n for n in agenda if int(n.get('id')) != note_id]
    if len(new) == len(agenda):
        abort(404)
    save_agenda(new)
    return '', 204


@app.route('/api/agenda/<int:note_id>/complete', methods=['PUT'])
def api_complete(note_id):
    agenda = load_agenda()
    for n in agenda:
        if int(n.get('id')) == note_id:
            n['completed'] = True
            n['triggered'] = True
            save_agenda(agenda)
            return jsonify(n)
    abort(404)


if __name__ == '__main__':
    app.run(debug=True)
