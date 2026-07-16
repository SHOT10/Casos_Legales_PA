from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Expediente, Aseguradora, Juzgado, EstadoExpediente, Usuario
from ..auth_utils import token_required

expedientes_bp = Blueprint("expedientes", __name__)


@expedientes_bp.get("")
@token_required
def listar():
    """Lista expedientes con filtros opcionales por query string:
    ?estado=Pendiente&aseguradora=1&juzgado=2&q=texto
    """
    query = Expediente.query

    estado = request.args.get("estado")
    if estado:
        query = query.join(EstadoExpediente).filter(EstadoExpediente.nombre.ilike(estado))

    id_aseguradora = request.args.get("aseguradora", type=int)
    if id_aseguradora:
        query = query.filter(Expediente.id_aseguradora == id_aseguradora)

    id_juzgado = request.args.get("juzgado", type=int)
    if id_juzgado:
        query = query.filter(Expediente.id_juzgado == id_juzgado)

    texto = request.args.get("q")
    if texto:
        like = f"%{texto}%"
        query = query.filter(
            (Expediente.numero_expediente.ilike(like)) | (Expediente.asegurado_nombre.ilike(like))
        )

    expedientes = query.order_by(Expediente.creado_en.desc()).all()
    return jsonify([e.to_dict() for e in expedientes]), 200


@expedientes_bp.post("")
@token_required
def crear():
    data = request.get_json(silent=True) or {}
    requeridos = ["numero_expediente", "asegurado_nombre", "id_aseguradora", "id_juzgado", "id_estado"]
    faltantes = [c for c in requeridos if not data.get(c)]
    if faltantes:
        return jsonify(error=f"Campos requeridos faltantes: {', '.join(faltantes)}"), 400

    if Expediente.query.filter_by(numero_expediente=data["numero_expediente"]).first():
        return jsonify(error="Ya existe un expediente con ese número"), 409
    if not Aseguradora.query.get(data["id_aseguradora"]):
        return jsonify(error="id_aseguradora inválido"), 400
    if not Juzgado.query.get(data["id_juzgado"]):
        return jsonify(error="id_juzgado inválido"), 400
    if not EstadoExpediente.query.get(data["id_estado"]):
        return jsonify(error="id_estado inválido"), 400
    if data.get("id_usuario_asignado") and not Usuario.query.get(data["id_usuario_asignado"]):
        return jsonify(error="id_usuario_asignado inválido"), 400

    nuevo = Expediente(
        numero_expediente=data["numero_expediente"],
        asegurado_nombre=data["asegurado_nombre"],
        id_aseguradora=data["id_aseguradora"],
        id_juzgado=data["id_juzgado"],
        id_estado=data["id_estado"],
        id_usuario_asignado=data.get("id_usuario_asignado"),
        descripcion=data.get("descripcion"),
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


@expedientes_bp.get("/<int:id_expediente>")
@token_required
def obtener(id_expediente):
    e = Expediente.query.get_or_404(id_expediente)
    return jsonify(e.to_dict()), 200


@expedientes_bp.put("/<int:id_expediente>")
@token_required
def actualizar(id_expediente):
    e = Expediente.query.get_or_404(id_expediente)
    data = request.get_json(silent=True) or {}

    campos_simples = ["asegurado_nombre", "descripcion", "fecha_cierre"]
    for campo in campos_simples:
        if campo in data:
            setattr(e, campo, data[campo])

    if "id_aseguradora" in data:
        if not Aseguradora.query.get(data["id_aseguradora"]):
            return jsonify(error="id_aseguradora inválido"), 400
        e.id_aseguradora = data["id_aseguradora"]

    if "id_juzgado" in data:
        if not Juzgado.query.get(data["id_juzgado"]):
            return jsonify(error="id_juzgado inválido"), 400
        e.id_juzgado = data["id_juzgado"]

    if "id_estado" in data:
        if not EstadoExpediente.query.get(data["id_estado"]):
            return jsonify(error="id_estado inválido"), 400
        e.id_estado = data["id_estado"]

    if "id_usuario_asignado" in data:
        e.id_usuario_asignado = data["id_usuario_asignado"]

    db.session.commit()
    return jsonify(e.to_dict()), 200


@expedientes_bp.delete("/<int:id_expediente>")
@token_required
def eliminar(id_expediente):
    e = Expediente.query.get_or_404(id_expediente)
    db.session.delete(e)
    db.session.commit()
    return jsonify(mensaje="Expediente eliminado"), 200
