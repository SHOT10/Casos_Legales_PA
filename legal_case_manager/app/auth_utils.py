"""
Utilidades de autenticación.
Se usa PyJWT directamente (en lugar de Flask-JWT-Extended) para mantener
las dependencias mínimas y evitar conflictos de versión, cumpliendo el
mismo objetivo: emitir y validar tokens de sesión.
"""
from functools import wraps
from datetime import datetime, timedelta

import jwt
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(raw: str) -> str:
    return generate_password_hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return check_password_hash(hashed, raw)


def generate_token(id_usuario: int, usuario: str, rol: str) -> str:
    payload = {
        "sub": id_usuario,
        "usuario": usuario,
        "rol": rol,
        "exp": datetime.utcnow() + timedelta(minutes=current_app.config["JWT_EXP_MINUTES"]),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def token_required(fn):
    """Decorador que exige un Bearer token válido en el header Authorization."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify(error="Token de autorización faltante"), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify(error="El token ha expirado"), 401
        except jwt.InvalidTokenError:
            return jsonify(error="Token inválido"), 401
        request.usuario_actual = payload
        return fn(*args, **kwargs)
    return wrapper
