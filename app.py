import os
import logging
import logging.handlers
from logging import Formatter
from dotenv import load_dotenv
from flask import Flask, request, current_app, jsonify, redirect, url_for, render_template
from flask_cors import CORS
from blueprints.game import socketio, start_ball_update


load_dotenv()

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'secret!'
    CORS(app, resources={r"/*": {"origins": "*"}})

    from blueprints.site import app as site_app

    app.register_blueprint(site_app)
    
    with app.app_context():
        change_logger() # change the default logger
        start_ball_update()

    socketio.init_app(app, cors_allowed_origins="*")
    return app

def change_logger():
    # redefining default formatter https://flask.palletsprojects.com/en/stable/logging/
    formatter = Formatter("[%(asctime)s] %(levelname)-8s %(process)d %(thread)s %(name)s in %(filename)s %(funcName)s():%(lineno)d %(message)s")
    current_app.logger.handlers[0].setFormatter(formatter)
    current_app.logger.setLevel(logging.DEBUG)
    # Add a rotating file handler
    log_to_file = os.getenv('LOG_TO_FILE', 'false').lower() == 'true'
    if not log_to_file:
        return
    file_handler = logging.handlers.RotatingFileHandler(
        'app.log', maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    current_app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app = create_app(debug=True)
    socketio.run(app, port=5000, host="0.0.0.0", allow_unsafe_werkzeug=True)
