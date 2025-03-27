import uuid
from flask import current_app
# Stato del gioco e sessioni attive
game_sessions = {}

def generate_session_id():
    """Genera un ID di sessione unico"""
    return str(uuid.uuid4())

def create_game_session(session_id):
    """Crea una nuova sessione di gioco"""
    if session_exists(session_id):
        current_app.logger.error(f'session "{session_id}" already exists')
        return False

    game_sessions[session_id] = {
        'players': {'left': None, 'right': None},
        'game_state': {
            'paddleLeftY': 300,
            'paddleRightY': 300,
            'ballX': 400,
            'ballY': 300,
            'ballVelocityX': 200,
            'ballVelocityY': 200
        }
    }
    current_app.logger.info(f'new session created "{session_id}"')
    return True
        
def join_session(session_id, playerid):
    """Aggiunge un giocatore a una sessione di gioco"""
    if session_id not in game_sessions:
        current_app.logger.error(f'session "{session_id}" not found')
        return (False, 'Session not found')

    if is_session_full(session_id):
        current_app.logger.error(f'session "{session_id}" is full')
        return (False, 'Session is full')
    
    if game_sessions[session_id]['players']['left'] == None:
        game_sessions[session_id]['players']['left'] = playerid
        current_app.logger.info(f'player "{playerid}" joined session "{session_id}" as left')
        return (True, 'left')
    
    if game_sessions[session_id]['players']['right'] == None:
        game_sessions[session_id]['players']['right'] = playerid
        current_app.logger.info(f'player "{playerid}" joined session "{session_id}" as right')
        return (True, 'right')

def get_player_paddle(session_id, playerid):
    """Restituisce il paddle assegnato a un giocatore in una sessione di gioco"""
    if game_sessions[session_id]['players']['left'] == playerid:
        return 'left'
    if game_sessions[session_id]['players']['right'] == playerid:
        return 'right'
    return None

def get_players_count(session_id):
    """Restituisce il numero di giocatori in una sessione di gioco"""
    return len(game_sessions[session_id]['players'])

def get_game_state(session_id):
    """Restituisce lo stato di una sessione di gioco"""
    return game_sessions[session_id]['game_state']

def is_session_full(session_id):
    """Restituisce True se la sessione è piena, False altrimenti"""
    if session_exists(session_id):
        return game_sessions[session_id]['players']['left'] is not None and game_sessions[session_id]['players']['right'] is not None
    return False

def update_paddle(session_id, paddle, paddle_y):
    """Aggiorna la posizione di un paddle in una sessione di gioco"""
    if paddle == 'left':
        game_sessions[session_id]['game_state']['paddleLeftY'] = paddle_y
    elif paddle == 'right':
        game_sessions[session_id]['game_state']['paddleRightY'] = paddle_y

def leave_session(playerid):
    """Rimuove un giocatore da una sessione di gioco"""
    for session_id, session in game_sessions.items():
        if session['players']['left'] == playerid:
            session['players']['left'] = None
            current_app.logger.info(f'player "{playerid}" left session "{session_id}"')
            return (True, 'left')
        
        if session['players']['right'] == playerid:
            session['players']['right'] = None
            current_app.logger.info(f'player "{playerid}" left session "{session_id}"')
            return (True, 'right')

    current_app.logger.error(f'player "{playerid}" not found in any session')
    return (False, 'Player not found')

    return False

def session_exists(session_id):
    """Restituisce True se la sessione esiste, False altrimenti"""
    return session_id in game_sessions

def get_available_sessions():
    """Restituisce una lista delle sessioni attive"""
    return [{'session_id': session_id, 'players':session['players']} for session_id, session in game_sessions.items()]

def delete_sessions():
    """Elimina tutte le sessioni di gioco"""
    game_sessions.clear()
    current_app.logger.info('all sessions deleted')