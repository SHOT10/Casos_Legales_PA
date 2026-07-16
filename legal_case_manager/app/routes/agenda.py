from datetime import date
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Agenda, Expediente
from ..auth_utils import token_required

agenda_bp = Blueprint("agenda", __name__)


@agenda_bp.get("")
@token_required
def listar():
    """Lista eventos. Por defecto trae los del día actual (Agenda del día).
    Usar ?fecha=YYYY-MM-DD para otra fecha, o ?todos=1 para el listado completo.
    """
    query = Agenda.query
    if request.args.get("todos"):
        eventos = query.order_by(Agenda.fecha_evento).all()
        return jsonify([e.to_dict() for e in eventos]), 200

    fecha_str = request.args.get("fecha")
    fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
    eventos = query.filter(Agenda.fecha_evento == fecha).order_by(Agenda.hora_evento).all()
    return jsonify([e.to_dict() for e in eventos]), 200


@agenda_bp.post("")
@token_required
def crear():
    data = request.get_json(silent=True) or {}
    requeridos = ["id_expediente", "titulo", "fecha_evento"]
    faltantes = [c for c in requeridos if not data.get(c)]
    if faltantes:
        return jsonify(error=f"Campos requeridos faltantes: {', '.join(faltantes)}"), 400

    if not Expediente.query.get(data["id_expediente"]):
        return jsonify(error="id_expediente inválido"), 400

    nuevo = Agenda(
        id_expediente=data["id_expediente"],
        titulo=data["titulo"],
        descripcion=data.get("descripcion"),
        fecha_evento=date.fromisoformat(data["fecha_evento"]),
        hora_evento=data.get("hora_evento"),
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


@agenda_bp.put("/<int:id_evento>")
@token_required
def actualizar(id_evento):
    e = Agenda.query.get_or_404(id_evento)
    data = request.get_json(silent=True) or {}
    if "titulo" in data:
        e.titulo = data["titulo"]
    if "descripcion" in data:
        e.descripcion = data["descripcion"]
    if "fecha_evento" in data:
        e.fecha_evento = date.fromisoformat(data["fecha_evento"])
    if "hora_evento" in data:
        e.hora_evento = data["hora_evento"]
    if "completado" in data:
        e.completado = bool(data["completado"])
    db.session.commit()
    return jsonify(e.to_dict()), 200


@agenda_bp.delete("/<int:id_evento>")
@token_required
def eliminar(id_evento):
    e = Agenda.query.get_or_404(id_evento)
    db.session.delete(e)
    db.session.commit()
    return jsonify(mensaje="Evento eliminado"), 200
