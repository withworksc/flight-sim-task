from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flight_commands import generate_commands, update_init_value
import logging

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# 初始化日誌
logging.basicConfig(level=logging.INFO)

# 驗證輸入值的函數
def validate_input(value):
    if not isinstance(value.get('alt'), (int, float)) or not (2500 <= value['alt'] <= 38000):
        raise ValueError("Altitude must be between 2500 and 38000 feet")
    if not isinstance(value.get('hdg'), (int, float)) or not (0 <= value['hdg'] <= 360):
        raise ValueError("Heading must be between 0 and 360 degrees")
    if not isinstance(value.get('velocity'), (int, float)) or not (160 <= value['velocity'] <= 330):
        raise ValueError("Velocity must be between 160 and 330 knots")
    return True

@app.route('/')
def home():
    app.logger.info('Home route accessed')
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    app.logger.info('Generate endpoint accessed')
    
    try:
        data = request.get_json()
        app.logger.info(f'Received data: {data}')
        
        # 構建初始值
        init_value = {
            'alt': int(data.get('altitude')),
            'hdg': int(data.get('heading')),
            'velocity': int(data.get('velocity'))
        }
        
        # 驗證輸入值
        validate_input(init_value)
        
        app.logger.info(f"Initial values: {init_value}")
        
        # 生成指令
        commands = generate_commands(init_value)
        
        # 更新當前條件
        new_conditions = update_init_value(init_value.copy(), commands)
        
        # 驗證更新後的值
        validate_input(new_conditions)
        
        response = {
            'commands': [cmd['command'] for cmd in commands],
            'initial_conditions': new_conditions
        }
        
        app.logger.info(f'Sending response: {response}')
        return jsonify(response)
        
    except ValueError as ve:
        app.logger.error(f'Validation error: {str(ve)}')
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)