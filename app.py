import time
import uuid
from threading import Thread
from flask import Flask, request, current_app, jsonify, redirect, url_for, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Stato del gioco e sessioni attive
game_sessions = {}

def generate_session_id():
    """Genera un ID di sessione unico"""
    return str(uuid.uuid4())

def create_game_session(session_id):
    """Crea una nuova sessione di gioco"""
    if session_id in game_sessions:
        current_app.logger.error(f'session "{session_id}" already exists')
        return False

    game_sessions[session_id] = {
        'players': [],
        'game_state': {
            'paddleLeftY': 250,
            'paddleRightY': 300,
            'ballX': 400,
            'ballY': 300,
            'ballVelocityX': 200,
            'ballVelocityY': 200
        }
    }
    current_app.logger.info(f'new session created "{session_id}"')
    return True
        

def get_available_sessions():
    """Restituisce una lista delle sessioni attive"""
    return [{'session_id': session_id, 'players': len(session['players'])} for session_id, session in game_sessions.items()]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/lobby', methods=['GET'])
def lobby():
    """Restituisce tutte le sessioni di gioco disponibili"""
    sessions = get_available_sessions()
    return jsonify(sessions)

@app.route('/create_session', methods=['POST'])
def post_create_session():
    """Crea una nuova sessione di gioco"""
    session_id = generate_session_id()
    create_game_session(session_id)
    return redirect(url_for('lobby'))

@socketio.on('createSession')
def socket_create_session(data):
    """Crea una nuova sessione di gioco tramite WebSocket"""
    session_id = data['session_id'] if 'session_id' in data else generate_session_id()
    # session_id = generate_session_id()
    if create_game_session(session_id):
        socketio.emit('sessionCreated', {'session_id': session_id})
    else:
        emit('error', {'message': 'Sessione già presente'})

@app.route('/join_session/<session_id>', methods=['POST'])
def post_join_session(session_id):
    """Permette a un client di unirsi a una sessione esistente"""
    if session_id not in game_sessions:
        return jsonify({'error': 'Sessione non trovata'}), 404

    # Se la sessione è piena, non permettere l'accesso
    if len(game_sessions[session_id]['players']) >= 2:
        return jsonify({'error': 'La sessione è piena'}), 400

    players = game_sessions[session_id]['players']
    if len(players) == 0:
        players.append('left')
    elif len(players) == 1:
        players.append('right')

    return jsonify({'session_id': session_id, 'paddle': players[-1]}), 200

@socketio.on('joinSession')
def socket_join_session(data):
    """Permette a un client di unirsi a una sessione esistente tramite WebSocket"""
    session_id = data['session_id']
    current_app.logger.info(f'player {request.sid} wants to connect to session {session_id}')
    
    if session_id not in game_sessions:
        emit('error', {'message': 'Sessione non trovata'})
        return

    # Se la sessione è piena, non permettere l'accesso
    if len(game_sessions[session_id]['players']) >= 2:
        emit('error', {'message': 'La sessione è piena'})
        return

    players = game_sessions[session_id]['players']
    if len(players) == 0:
        players.append('left')
    elif len(players) == 1:
        players.append('right')

    socketio.emit('sessionJoined', {'session_id': session_id, 'paddle': players[-1]})
    # Notifica tutti i client connessi a quella sessione
    socketio.emit('gameState', game_sessions[session_id]['game_state'], to=session_id)
    
@socketio.on('connect')
def handle_connect():
    current_app.logger.info(f'Client connected: {request.sid}')

    # Per ora, il client si unisce a una sessione esistente o può essere uno spettatore
    # In futuro si può migliorare con una logica per l'unione a sessioni specifiche
    session_id = request.args.get('session_id', None)

    if not session_id or session_id not in game_sessions:
        # Se non viene fornito un session_id valido, il client è uno spettatore
        session_id = None

    if session_id:
        # Gestiamo l'aggiunta di un client alla sessione di gioco
        players = game_sessions[session_id]['players']
        if len(players) == 0:
            players.append('left')
        elif len(players) == 1:
            players.append('right')

        emit('assignPaddle', {'session_id': session_id, 'paddle': players[-1]})
    emit('gameState', game_sessions[session_id]['game_state'] if session_id else {})

@socketio.on('disconnect')
def handle_disconnect():
    current_app.logger.info(f'Client {request.sid} disconnected')
    for session_id, session in game_sessions.items():
        if request.sid in session['players']:
            session['players'].remove(request.sid)
            break

@socketio.on('updatePaddle')
def handle_update_paddle(data):
    session_id = data['session_id']
    paddle = data['paddle']
    paddle_y = data['paddleY']

    # Aggiorna il paddle solo se appartiene al client
    if paddle == 'left' and 'left' in game_sessions[session_id]['players']:
        game_sessions[session_id]['game_state']['paddleLeftY'] = paddle_y
    elif paddle == 'right' and 'right' in game_sessions[session_id]['players']:
        game_sessions[session_id]['game_state']['paddleRightY'] = paddle_y

def update_ball(session_id):
    # Movimento della palla (aggiornamento lato server)
    game_state = game_sessions[session_id]['game_state']
    game_state['ballX'] += game_state['ballVelocityX'] / 60
    game_state['ballY'] += game_state['ballVelocityY'] / 60

    # Collisione con bordi superiore e inferiore
    if game_state['ballY'] <= 0 or game_state['ballY'] >= 600:
        game_state['ballVelocityY'] = -game_state['ballVelocityY']

    # Collisione con i paddle
    if (game_state['ballX'] <= 60 and game_state['paddleLeftY'] <= game_state['ballY'] <= game_state['paddleLeftY'] + 100) or \
       (game_state['ballX'] >= 740 and game_state['paddleRightY'] <= game_state['ballY'] <= game_state['paddleRightY'] + 100):
        game_state['ballVelocityX'] = -game_state['ballVelocityX']

    # print(f"Ball updated: X={game_state['ballX']} Y={game_state['ballY']}")
    # Invia lo stato aggiornato a tutti i client della sessione
    socketio.emit('gameState', game_state, to=session_id)

def ball_update_loop():
    while True:
        for session_id in game_sessions:
            update_ball(session_id)
        time.sleep(1 / 60)  # Sincronizzazione a ~60 FPS

def start_ball_update():
    thread = Thread(target=ball_update_loop)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    # Avvia il ciclo di aggiornamento della palla in background
    start_ball_update()
    socketio.run(app, debug=True, port=5000)
