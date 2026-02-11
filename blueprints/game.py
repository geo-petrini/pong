import time
from threading import Thread, Event
import random

from flask import request
from flask import current_app
from flask import jsonify

from flask_socketio import SocketIO
from flask_socketio import emit, join_room, leave_room
from benedict import benedict
import modules.session_utils as su

socketio = SocketIO()
stop_event = Event()

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

    socketio.emit('sessionJoined', {'session_id': session_id, 'paddle': paddle, 'to':request.sid})
    # Notifica tutti i client connessi a quella sessione
    socketio.emit('gameState', {'state':su.get_game_state(session_id).to_dict(), 'to':session_id})
    
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
        socketio.emit('gameState', {'state':su.get_game_state(session_id).to_dict(), 'to':session_id})
    else:
        emit('error', {'message': 'Sessione non trovata'})

def update_ball(game_state):
    # Movimento della palla (aggiornamento lato server)
    # game_state = su.get_game_state(session_id)
    game_state.ball.x += game_state.ball.x / 60
    game_state.ball.y += game_state.ball.y / 60

    # Collisione con bordi
    _check_collision_ball_top(game_state)
    _check_collision_ball_bottom(game_state)
    _check_collision_ball_left(game_state)
    _check_collision_ball_right(game_state)

def _reset_ball(game_state):
    game_state.ball.x = current_app.config['GAME_WIDTH']/2  # Reset to center (half of the width)
    game_state.ball.y = current_app.config['GAME_HEIGHT']/2  # Reset to center (half of the height)
    game_state.ball.velocity.x = -game_state.ball.velocity.x  # Reverse direction
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
     if game_state.ball.x <= 0:
        su.end_round(game_state, 'right')  # Il giocatore destro vince il round
        _reset_ball(game_state)  
        
def _check_collision_ball_right(game_state):
    # Collisione con bordo destro
     if game_state.ball.x >= current_app.config['GAME_WIDTH']:
        su.end_round(game_state, 'left')  # Il giocatore sinistro vince il round
        _reset_ball(game_state)  

def _check_collision_paddle_left(game_state):
    pass

def update_loop(app):
    dt = 1/60.0  # 60 FPS
    with app.app_context():
        while not stop_event.is_set():
            for session_id in su.game_sessions.keys():
                try:
                    game_state = su.get_game_state(session_id)
                    if not game_state:
                        continue
                    
                    if not su.is_session_full(session_id):
                        continue

                    if game_state.current_round == None:
                        current_app.logger.warning(f'Session {session_id} has no rounds initialized, starting round')
                        su.start_round(game_state)

                    if game_state.current_round and game_state.current_round.countdown > 0:
                        # Countdown prima dell'inizio del round
                        game_state.current_round.countdown -= dt  # Decrementa il countdown
                    else:    
                        update_ball(game_state)
                    # Invia lo stato aggiornato a tutti i client della sessione
                    try:
                        socketio.emit('gameState', {'state':game_state.to_dict(), 'to':session_id})
                    except Exception as e:
                        current_app.logger.exception(f"Errore durante l'emissione dello stato del gioco per la sessione {session_id}: {e}")                
                except Exception as e:
                    current_app.logger.exception(f"Errore nel loop: sessione {session_id}: {e}")
            time.sleep(dt)  # Sincronizzazione a ~60 FPS

def start_loop():
    current_app.logger.info('Creating background update loop')

    socketio.start_background_task(update_loop, current_app._get_current_object())
    # thread = Thread(target=update_loop)
    # thread.daemon = True
    # thread.start()

def stop_loop():
    stop_event.set()