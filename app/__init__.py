import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import secrets
from flask import g


db = SQLAlchemy()
csrf = CSRFProtect()  # Inisialisasi CSRF

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ini_rahasia'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

    # ✨ Konfigurasi cookie untuk keamanan
    app.config.update(
        SESSION_COOKIE_SAMESITE='Strict',   # Batasi cookie agar tidak ikut terkirim cross-site
        SESSION_COOKIE_SECURE=True,         # Cookie hanya dikirim lewat HTTPS (kalau HTTPS)
        SESSION_COOKIE_HTTPONLY=True        # Cookie tidak bisa diakses oleh JS (mengurangi XSS)
    )

    db.init_app(app)
    csrf.init_app(app)  # Aktifkan CSRF protection

    from .routes import main
    app.register_blueprint(main)

    # Setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # Hapus emoji agar tidak error di Windows
    app.logger.info('Todo App started')

    @app.before_request
    def set_nonce():
        g.nonce = secrets.token_urlsafe(16)

    # ✨ Tambahkan HTTP header keamanan lewat after_request
    @app.after_request
    def set_secure_headers(response):
        nonce = g.get("nonce")
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdn.jsdelivr.net 'nonce-{nonce}'; "
            f"style-src 'self' https://cdn.jsdelivr.net 'nonce-{nonce}'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers['Content-Security-Policy'] = csp
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    return app
