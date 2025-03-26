from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Dati del gioco: posizioni iniziali di paddle e palla
game_state = {
    'paddleLeftY': 300,
    'paddleRightY': 300,
    'ballX': 400,
    'ballY': 300,
    'ballVelocityX': 200,
    'ballVelocityY': 200
}

@app.route('/')
def home():
    return "Welcome to the Pong Server!"

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Invia lo stato del gioco quando un client si connette
    emit('gameState', game_state)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('updatePaddle')
def handle_update_paddle(data):
    # Solo aggiornare la posizione del paddle del client che invia l'aggiornamento
    if data['paddle'] == 'left':
        game_state['paddleLeftY'] = data['paddleY']
    elif data['paddle'] == 'right':
        game_state['paddleRightY'] = data['paddleY']

    # Gestisci il movimento della palla
    game_state['ballX'] += game_state['ballVelocityX'] / 60
    game_state['ballY'] += game_state['ballVelocityY'] / 60

    # Collisione con i bordi superiore e inferiore
    if game_state['ballY'] <= 0 or game_state['ballY'] >= 600:
        game_state['ballVelocityY'] = -game_state['ballVelocityY']

    # Collisione con i paddle
    if (game_state['ballX'] <= 60 and game_state['ballY'] >= game_state['paddleLeftY'] and game_state['ballY'] <= game_state['paddleLeftY'] + 100) or \
       (game_state['ballX'] >= 740 and game_state['ballY'] >= game_state['paddleRightY'] and game_state['ballY'] <= game_state['paddleRightY'] + 100):
        game_state['ballVelocityX'] = -game_state['ballVelocityX']

    # Invia lo stato del gioco aggiornato a tutti i client
    emit('gameState', game_state, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
