from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Juzgado
from ..auth_utils import token_required

juzgados_bp = Blueprint("juzgados", __name__)


@juzgados_bp.get("")
@token_required
def listar():
    return jsonify([j.to_dict() for j in Juzgado.query.all()]), 200


@juzgados_bp.post("")
@token_required
def crear():
    data = request.get_json(silent=True) or {}
    if not data.get("nombre"):
        return jsonify(error="El campo 'nombre' es requerido"), 400
    if Juzgado.query.filter_by(nombre=data["nombre"]).first():
        return jsonify(error="Ya existe un juzgado con ese nombre"), 409

    nuevo = Juzgado(nombre=data["nombre"], circuito=data.get("circuito"))
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


@juzgados_bp.get("/<int:id_juzgado>")
@token_required
def obtener(id_juzgado):
    j = Juzgado.query.get_or_404(id_juzgado)
    return jsonify(j.to_dict()), 200


@juzgados_bp.put("/<int:id_juzgado>")
@token_required
def actualizar(id_juzgado):
    j = Juzgado.query.get_or_404(id_juzgado)
    data = request.get_json(silent=True) or {}
    for campo in ("nombre", "circuito", "activo"):
        if campo in data:
            setattr(j, campo, data[campo])
    db.session.commit()
    return jsonify(j.to_dict()), 200


@juzgados_bp.delete("/<int:id_juzgado>")
@token_required
def eliminar(id_juzgado):
    j = Juzgado.query.get_or_404(id_juzgado)
    j.activo = False
    db.session.commit()
    return jsonify(mensaje="Juzgado desactivado"), 200
