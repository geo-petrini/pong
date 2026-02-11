from flask import render_template
from flask import url_for
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import request
from flask import current_app
from flask import send_from_directory
from flask import jsonify
import modules.session_utils as su

app = Blueprint('site', __name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'media/favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/sessions')
def sessions():
    sessions = su.get_available_sessions()
    return render_template('sessions.html', sessions=sessions)

@app.route('/sessions', methods=['DELETE'])
def delete_sessions():
    current_app.logger.info('deleting all sessions')
    su.delete_sessions()
    return jsonify({'message': 'ok'})

@app.route('/lobby', methods=['GET'])
def lobby():
    """Restituisce tutte le sessioni di gioco disponibili"""
    sessions = su.get_available_sessions()
    return jsonify(sessions)

@app.route('/config')
def get_config():
    config = {
        'GAME_WIDTH':current_app.config['GAME_WIDTH'],
        'GAME_HEIGHT':current_app.config['GAME_HEIGHT'],
        'PADDLE_WIDHT':current_app.config['PADDLE_WIDHT'],       
        'PADDLE_HEIGHT':current_app.config['PADDLE_HEIGHT'],    
        'PADDLE_OFFSET':current_app.config['PADDLE_OFFSET'],    
        'PADDLE_VELOCITY':current_app.config['PADDLE_VELOCITY'],    
        'BALL_SIZE':current_app.config['BALL_SIZE'],
        'BALL_VELOCITY':current_app.config['BALL_VELOCITY']
    }
    return jsonify(config)


@app.route("/config", methods=['POST'])
def set_config():
    data = request.json
    if data:
        for key, value in data.items():
            if key in current_app.config:
                current_app.config[key] = value
    return jsonify({"ok": True})