from functools import wraps
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)


def _mock_get_things_from_db(id=None):
    things = [{'id': '2ce41c1a-095e-4e1f-8c08-59bfd89fa806', 'name': 'thing1'},
              {'id': 'c1a68009-97f0-4ca9-94fd-c300b63314b1', 'name': 'thing2'}]
    if id:
        thing = [t for t in things if t['id'] == id]
        return thing[0] if thing else None
    return things


def handle_errors(f, is_json_response=True):
    @wraps(f)
    def decorated(*args, **kwargs):
        response = {}
        try:
            response = f(*args, **kwargs)
        except Exception as e:
            print(str(e))
            response = {
                'body': {
                    'message': str(e)
                },
                'status_code': 500
            }
        return jsonify(response['body']), \
            response['status_code'], \
            response.get('headers', {})
    return decorated


@app.route('/health', methods=['GET'])
@handle_errors
def health():
    return {
        'status_code': 200,
        'body': {
            'status': 'success'
        }
    }


@app.route('/things', methods=['GET'])
@handle_errors
def get_things():
    return {
        'status_code': 200,
        'body': _mock_get_things_from_db()
    }


@app.route('/things', methods=['POST'])
@handle_errors
def post_things():
    if not request.get_json().get('name'):
        return {
            'status_code': 400,
            'headers': {},
            'body': {'message': 'Missing key: name.'}
        }
    return {
        'status_code': 201,
        'headers': {},
        'body': {'id': str(uuid.uuid4()), 'name': request.get_json()['name']}
    }


@app.route('/things/<thing_id>', methods=['GET'])
@handle_errors
def get_thing(thing_id):
    thing = _mock_get_things_from_db(id=thing_id)
    if not thing:
        return {
            'status_code': 404,
            'body': {
                'message': 'Thing not found.'}
        }
    return {
        'status_code': 200,
        'headers': {},
        'body': {'id': thing['id'],
                 'name': thing['name']}
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
