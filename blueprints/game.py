import time
from threading import Thread
import random

from flask import request
from flask import current_app
from flask import jsonify

from flask_socketio import SocketIO
from flask_socketio import emit, join_room, leave_room

import modules.session_utils as su

socketio = SocketIO()


# TODO check if it could be better using rooms
# TODO use global variables to store the game size and other default values (like paddles x position)

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
        # current_app.logger.debug(f'emitting state:{su.get_game_state(session_id).to_json()}')
        socketio.emit('gameState', {'state':su.get_game_state(session_id).to_json(), 'to':session_id})
    else:
        emit('error', {'message': 'Sessione non trovata'})

def update_ball(session_id):
    # Movimento della palla (aggiornamento lato server)
    game_state = su.get_game_state(session_id)
    game_state.ball.x += game_state['ballVelocityX'] / 60
    game_state.ball.y += game_state['ballVelocityY'] / 60

    # Collisione con bordi
    _check_collision_ball_top(game_state)
    _check_collision_ball_bottom(game_state)
    _check_collision_ball_left(game_state)
    _check_collision_ball_right(game_state)

    # Invia lo stato aggiornato a tutti i client della sessione
    try:
        socketio.emit('gameState', {'state':game_state.to_json(), 'to':session_id})
    except Exception as e:
        current_app.logger.exception(f"Errore durante l'emissione dello stato del gioco per la sessione {session_id}: {e}")

def _reset_ball(game_state):
    game_state.ball.x = current_app.config['GAME_WIDTH']/2  # Reset to center (half of the width)
    game_state.ball.y = current_app.config['GAME_HEIGHT']/2  # Reset to center (half of the height)
    game_state.ball.velocity.x = -game_state['ballVelocityX']  # Reverse direction
    game_state.ball.velocity.y = random.choice([-200, 200])  # Reset vertical velocity to a random direction    

def _check_collision_ball_top(game_state):
    # Collisione con bordo superiore
    if game_state.ball.y <= 0:
        game_state.ball.velocity.y = -game_state.ball.velocity.y
        
def _check_collision_ball_bottom(game_state):
    # Collisione con bordo inferiore
     if game_state.ball.y >= current_app.config['GAME_WIDTH']:
        game_state.ball.velocity.y = -game_state.ball.velocity.y    

def _check_collision_ball_left(game_state):
    # Collisione con bordo sinistro
     if game_state.ball.x >= 0:
        _reset_ball(game_state)  
        
def _check_collision_ball_right(game_state):
    # Collisione con bordo destro
     if game_state.ball.x >= current_app.config['GAME_WIDTH']:
        _reset_ball(game_state)  

def _check_collision_paddle_left(game_state):
    # if game_state['ballX'] = game_state["pa"]
    pass

def ball_update_loop():
    while True:
        for session_id in su.game_sessions.keys():
            try:
                update_ball(session_id)
            except Exception as e:
                current_app.logger.exception(f"Errore durante l'aggiornamento della palla per la sessione {session_id}: {e}")
        time.sleep(1 / 60)  # Sincronizzazione a ~60 FPS

def start_ball_update():
    current_app.logger.info('Creating background update loop')
    thread = Thread(target=ball_update_loop)
    thread.daemon = True
    thread.start()
