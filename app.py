from flask import Flask, jsonify, request
from flask_cors import CORS
from flight_commands import generate_commands, update_init_value
import logging

app = Flask(__name__)
CORS(app)

# 設置日誌
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    app.logger.info('Home route accessed')
    return 'Flight Commands API is running'

@app.route('/generate', methods=['POST'])
def generate():
    app.logger.info('Generate endpoint accessed')
    try:
        data = request.get_json()
        app.logger.info(f'Received data: {data}')
        
        init_value = {
            'alt': data.get('altitude', 10000),
            'hdg': data.get('heading', 360),
            'velocity': data.get('velocity', 250)
        }
        
        commands = generate_commands(init_value)
        new_init_value = update_init_value(commands)
        
        command_strings = [cmd['command'] for cmd in commands]
        
        response = {
            'commands': command_strings,
            'initial_conditions': new_init_value
        }
        app.logger.info(f'Sending response: {response}')
        return jsonify(response)
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')