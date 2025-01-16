from flask import Flask, jsonify, request
from flask_cors import CORS
from flight_commands import generate_commands, update_init_value

app = Flask(__name__)
CORS(app)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        init_value = {
            'alt': data.get('altitude', 10000),
            'hdg': data.get('heading', 360),
            'velocity': data.get('velocity', 250)
        }
        
        commands = generate_commands(init_value)
        new_init_value = update_init_value(commands)
        
        command_strings = [cmd['command'] for cmd in commands]
        
        return jsonify({
            'commands': command_strings,
            'initial_conditions': new_init_value
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')