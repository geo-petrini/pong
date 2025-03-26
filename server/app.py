from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

game_state = {
    'paddleLeftY': 300,
    'paddleRightY': 300,
    'ballX': 400,
    'ballY': 300,
    'ballVelocityX': 200,
    'ballVelocityY': 200
}

players = {}  # Memorizza l'assegnazione dei paddle ai client

@app.route('/')
def home():
    return "Welcome to the Pong Server!"

@socketio.on('connect')
def handle_connect():
    print('Client connected')

    # Assegna un paddle al nuovo giocatore
    if 'left' not in players.values():
        paddle_side = 'left'
    elif 'right' not in players.values():
        paddle_side = 'right'
    else:
        paddle_side = 'spectator'  # Se entrambi i paddle sono occupati, diventa spettatore

    players[request.sid] = paddle_side  # Assegna il paddle al client
    emit('assignPaddle', {'paddle': paddle_side})  # Invia il lato al client
    emit('gameState', game_state)

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client {request.sid} disconnected')
    if request.sid in players:
        del players[request.sid]  # Libera il paddle

@socketio.on('updatePaddle')
def handle_update_paddle(data):
    if data['paddle'] == 'left' and players.get(request.sid) == 'left':
        game_state['paddleLeftY'] = data['paddleY']
    elif data['paddle'] == 'right' and players.get(request.sid) == 'right':
        game_state['paddleRightY'] = data['paddleY']

    game_state['ballX'] += game_state['ballVelocityX'] / 60
    game_state['ballY'] += game_state['ballVelocityY'] / 60

    if game_state['ballY'] <= 0 or game_state['ballY'] >= 600:
        game_state['ballVelocityY'] = -game_state['ballVelocityY']

    if (game_state['ballX'] <= 60 and game_state['ballY'] >= game_state['paddleLeftY'] and game_state['ballY'] <= game_state['paddleLeftY'] + 100) or \
       (game_state['ballX'] >= 740 and game_state['ballY'] >= game_state['paddleRightY'] and game_state['ballY'] <= game_state['paddleRightY'] + 100):
        game_state['ballVelocityX'] = -game_state['ballVelocityX']

    emit('gameState', game_state, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
