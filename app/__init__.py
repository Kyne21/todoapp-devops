import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ini_rahasia'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    # 🔧 Logging dasar untuk observability
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=3)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('📋 Todo App started')

    return app
