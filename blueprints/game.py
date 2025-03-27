import time
from threading import Thread

from flask import request
from flask import current_app
from flask import jsonify

from flask_socketio import SocketIO
from flask_socketio import emit, join_room, leave_room

import modules.session_utils as su

socketio = SocketIO()

# TODO check if it could be better using rooms

@socketio.on('createSession')
def socket_create_session(data):
    """Crea una nuova sessione di gioco tramite WebSocket"""
    session_id = data['session_id'] if 'session_id' in data else su.generate_session_id()

    if su.create_game_session(session_id):
        socketio.emit('sessionCreated', {'session_id': session_id, 'to':request.sid} )
    else:
        emit('error', {'message': 'Sessione già presente'})

    # Se la sessione è piena, non permettere l'accesso
    if su.is_session_full(session_id):
        return jsonify({'error': 'La sessione è piena'}), 400

    return jsonify({'session_id': session_id}), 200

@socketio.on('joinSession')
def socket_join_session(data):
    """Permette a un client di unirsi a una sessione esistente tramite WebSocket"""
    session_id = data['session_id']
    current_app.logger.info(f'player {request.sid} wants to connect to session {session_id}')
    
    (result, message) = su.join_session(session_id, request.sid)
    if not result:
        emit('error', {'message': message})
        return

    paddle = su.get_player_paddle(session_id, request.sid)

    # TODO use the to argument somehow
    socketio.emit('sessionJoined', {'session_id': session_id, 'paddle': paddle, 'to':request.sid})
    # Notifica tutti i client connessi a quella sessione
    socketio.emit('gameState', {'state':su.get_game_state(session_id), 'to':session_id})
    
@socketio.on('connect')
def handle_connect():
    current_app.logger.info(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    (result, message) = su.leave_session(request.sid)
    current_app.logger.info(f'Client {request.sid} disconnected {result}, {message}')

@socketio.on('updatePaddle')
def handle_update_paddle(data):
    session_id = data['session_id'] if 'session_id' in data else None
    paddle = data['paddle'] if 'paddle' in data else None
    paddle_y = data['paddleY'] if 'paddleY' in data else None

    if not session_id or not paddle or not paddle_y:
        emit('error', {'message': 'Dati mancanti'})
        return
    
    if su.session_exists(session_id):
        su.update_paddle(session_id, paddle, paddle_y)
        socketio.emit('gameState', {'state':su.get_game_state(session_id), 'to':session_id})
    else:
        emit('error', {'message': 'Sessione non trovata'})

def update_ball(session_id):
    # Movimento della palla (aggiornamento lato server)
    game_state = su.get_game_state(session_id)
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
    try:
        socketio.emit('gameState', {'state':game_state, 'to':session_id})
    except Exception as e:
        current_app.logger.exception(f"Errore durante l'emissione dello stato del gioco per la sessione {session_id}: {e}")

def ball_update_loop():
    while True:
        for session_id in su.game_sessions.keys():
            try:
                update_ball(session_id)
            except Exception as e:
                current_app.logger.exception(f"Errore durante l'aggiornamento della palla per la sessione {session_id}: {e}")
        time.sleep(1 / 60)  # Sincronizzazione a ~60 FPS

def start_ball_update():
    thread = Thread(target=ball_update_loop)
    thread.daemon = True
    thread.start()
