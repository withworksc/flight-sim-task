from flask import Flask, render_template, jsonify, request
from flight_commands import generate_commands, update_init_value

app = Flask(__name__)

@app.route('/')
def home():
    print("Accessing home page")  # Debug print
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    print("Generate endpoint called")  # Debug print
    try:
        # Get current conditions from request
        data = request.get_json()
        print("Received data:", data)  # Debug print
        
        if data is None:
            return jsonify({'error': 'No data received'}), 400
        
        init_value = {
            'alt': data.get('altitude', 10000),
            'hdg': data.get('heading', 360),
            'velocity': data.get('velocity', 250)
        }
        print("Init value:", init_value)  # Debug print
        
        # Generate commands
        commands = generate_commands(init_value)
        print("Generated commands:", commands)  # Debug print
        
        # Update initial values
        new_init_value = update_init_value(commands)
        print("New init value:", new_init_value)  # Debug print
        
        response_data = {
            'commands': [cmd['command'] for cmd in commands],
            'initial_conditions': new_init_value
        }
        print("Sending response:", response_data)  # Debug print
        
        return jsonify(response_data)
    except Exception as e:
        print("Error occurred:", str(e))  # Debug print
        import traceback
        print("Traceback:", traceback.format_exc())  # Print full error traceback
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)