from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Usuario, Rol
from ..auth_utils import hash_password, verify_password, generate_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/registro")
def registro():
    data = request.get_json(silent=True) or {}
    requeridos = ["nombre_completo", "usuario", "password", "id_rol"]
    faltantes = [c for c in requeridos if not data.get(c)]
    if faltantes:
        return jsonify(error=f"Campos requeridos faltantes: {', '.join(faltantes)}"), 400

    if Usuario.query.filter_by(usuario=data["usuario"]).first():
        return jsonify(error="El nombre de usuario ya existe"), 409

    if not Rol.query.get(data["id_rol"]):
        return jsonify(error="id_rol inválido"), 400

    nuevo = Usuario(
        nombre_completo=data["nombre_completo"],
        usuario=data["usuario"],
        correo=data.get("correo"),
        password_hash=hash_password(data["password"]),
        id_rol=data["id_rol"],
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    usuario = data.get("usuario")
    password = data.get("password")
    if not usuario or not password:
        return jsonify(error="usuario y password son requeridos"), 400

    user = Usuario.query.filter_by(usuario=usuario, activo=True).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify(error="Credenciales inválidas"), 401

    token = generate_token(user.id_usuario, user.usuario, user.rol.nombre)
    return jsonify(token=token, usuario=user.to_dict()), 200
