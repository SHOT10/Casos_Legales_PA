from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Usuario, Rol
from ..auth_utils import token_required, hash_password

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.get("")
@token_required
def listar():
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios]), 200


@usuarios_bp.get("/<int:id_usuario>")
@token_required
def obtener(id_usuario):
    u = Usuario.query.get_or_404(id_usuario)
    return jsonify(u.to_dict()), 200


@usuarios_bp.put("/<int:id_usuario>")
@token_required
def actualizar(id_usuario):
    u = Usuario.query.get_or_404(id_usuario)
    data = request.get_json(silent=True) or {}

    if "nombre_completo" in data:
        u.nombre_completo = data["nombre_completo"]
    if "correo" in data:
        u.correo = data["correo"]
    if "id_rol" in data:
        if not Rol.query.get(data["id_rol"]):
            return jsonify(error="id_rol inválido"), 400
        u.id_rol = data["id_rol"]
    if "activo" in data:
        u.activo = bool(data["activo"])
    if "password" in data and data["password"]:
        u.password_hash = hash_password(data["password"])

    db.session.commit()
    return jsonify(u.to_dict()), 200


@usuarios_bp.delete("/<int:id_usuario>")
@token_required
def eliminar(id_usuario):
    u = Usuario.query.get_or_404(id_usuario)
    u.activo = False  # baja lógica, preserva integridad referencial
    db.session.commit()
    return jsonify(mensaje="Usuario desactivado"), 200
