from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flight_commands import generate_commands, update_init_value
import logging

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# 設置日誌
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    app.logger.info('Home route accessed')
    # 返回 index.html 作為首頁
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    app.logger.info('Generate endpoint accessed')
    try:
        data = request.get_json()
        app.logger.info(f'Received data: {data}')
        
        # 取得初始條件，並提供預設值
        current_value = {
            'alt': data.get('altitude', 10000),
            'hdg': data.get('heading', 360),
            'velocity': data.get('velocity', 250)
        }

        # 調用命令生成函數
        commands = generate_commands(current_value)
        # 使用當前值更新到新的狀態
        new_value = update_init_value(current_value.copy(), commands)
        
        # 提取指令內容
        command_strings = [cmd['command'] for cmd in commands]
        
        # 準備回應
        response = {
            'commands': command_strings,
            'initial_conditions': new_value  # 回傳更新後的值
        }
        app.logger.info(f'Sending response: {response}')
        return jsonify(response)
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)
