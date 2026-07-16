from datetime import date
from flask import Blueprint, jsonify
from sqlalchemy import func
from ..extensions import db
from ..models import Expediente, EstadoExpediente, Agenda
from ..auth_utils import token_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("")
@token_required
def resumen():
    conteos = (
        db.session.query(EstadoExpediente.nombre, func.count(Expediente.id_expediente))
        .outerjoin(Expediente, Expediente.id_estado == EstadoExpediente.id_estado)
        .group_by(EstadoExpediente.nombre)
        .all()
    )
    contadores = {nombre: total for nombre, total in conteos}

    hoy = date.today()
    agenda_hoy = Agenda.query.filter(Agenda.fecha_evento == hoy).order_by(Agenda.hora_evento).all()

    return jsonify(
        fecha=hoy.isoformat(),
        contadores=contadores,
        agenda_del_dia=[a.to_dict() for a in agenda_hoy],
    ), 200
