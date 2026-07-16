from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Aseguradora
from ..auth_utils import token_required

aseguradoras_bp = Blueprint("aseguradoras", __name__)


@aseguradoras_bp.get("")
@token_required
def listar():
    return jsonify([a.to_dict() for a in Aseguradora.query.all()]), 200


@aseguradoras_bp.post("")
@token_required
def crear():
    data = request.get_json(silent=True) or {}
    if not data.get("nombre"):
        return jsonify(error="El campo 'nombre' es requerido"), 400
    if Aseguradora.query.filter_by(nombre=data["nombre"]).first():
        return jsonify(error="Ya existe una aseguradora con ese nombre"), 409

    nueva = Aseguradora(nombre=data["nombre"], telefono=data.get("telefono"), correo=data.get("correo"))
    db.session.add(nueva)
    db.session.commit()
    return jsonify(nueva.to_dict()), 201


@aseguradoras_bp.get("/<int:id_aseguradora>")
@token_required
def obtener(id_aseguradora):
    a = Aseguradora.query.get_or_404(id_aseguradora)
    return jsonify(a.to_dict()), 200


@aseguradoras_bp.put("/<int:id_aseguradora>")
@token_required
def actualizar(id_aseguradora):
    a = Aseguradora.query.get_or_404(id_aseguradora)
    data = request.get_json(silent=True) or {}
    for campo in ("nombre", "telefono", "correo", "activo"):
        if campo in data:
            setattr(a, campo, data[campo])
    db.session.commit()
    return jsonify(a.to_dict()), 200


@aseguradoras_bp.delete("/<int:id_aseguradora>")
@token_required
def eliminar(id_aseguradora):
    a = Aseguradora.query.get_or_404(id_aseguradora)
    a.activo = False
    db.session.commit()
    return jsonify(mensaje="Aseguradora desactivada"), 200
