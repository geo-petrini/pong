from flask import Flask, request, current_app
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Stato del gioco
game_state = {
    'paddleLeftY': 300,
    'paddleRightY': 300,
    'ballX': 400,
    'ballY': 300,
    'ballVelocityX': 200,
    'ballVelocityY': 200
}

# Memorizza l'assegnazione dei paddle ai client
players = {}

@app.route('/')
def home():
    return "Welcome to the Pong Server!"

@socketio.on('connect')
def handle_connect():
    current_app.logger.info('Client connected')

    # Assegna un paddle al nuovo giocatore
    if 'left' not in players.values():
        paddle_side = 'left'
    elif 'right' not in players.values():
        paddle_side = 'right'
    else:
        paddle_side = 'spectator'

    players[request.sid] = paddle_side
    emit('assignPaddle', {'paddle': paddle_side})
    emit('gameState', game_state)

    current_app.logger.info(f'Paddle assegnato: {paddle_side} per client {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    current_app.logger.info(f'Client {request.sid} disconnected')
    if request.sid in players:
        del players[request.sid]
        current_app.logger.info(f'Paddle liberato dal client {request.sid}')

@socketio.on('updatePaddle')
def handle_update_paddle(data):
    # Aggiorna la posizione del paddle solo se il client ha il permesso
    if data['paddle'] == 'left' and players.get(request.sid) == 'left':
        game_state['paddleLeftY'] = data['paddleY']
    elif data['paddle'] == 'right' and players.get(request.sid) == 'right':
        game_state['paddleRightY'] = data['paddleY']

    # Aggiorna la posizione della palla
    game_state['ballX'] += game_state['ballVelocityX'] / 60
    game_state['ballY'] += game_state['ballVelocityY'] / 60

    # Collisione con i bordi superiore e inferiore
    if game_state['ballY'] <= 0 or game_state['ballY'] >= 600:
        game_state['ballVelocityY'] = -game_state['ballVelocityY']

    # Collisione con i paddle
    if (game_state['ballX'] <= 60 and game_state['paddleLeftY'] <= game_state['ballY'] <= game_state['paddleLeftY'] + 100) or \
       (game_state['ballX'] >= 740 and game_state['paddleRightY'] <= game_state['ballY'] <= game_state['paddleRightY'] + 100):
        game_state['ballVelocityX'] = -game_state['ballVelocityX']

    # Invia lo stato aggiornato a tutti i client
    emit('gameState', game_state, broadcast=True)

    current_app.logger.debug(f"Update paddle {data['paddle']} by {request.sid}")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
