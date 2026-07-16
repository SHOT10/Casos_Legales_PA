from flask import Blueprint, jsonify
from ..models import EstadoExpediente
from ..auth_utils import token_required

catalogos_bp = Blueprint("catalogos", __name__)


@catalogos_bp.get("/estados")
@token_required
def estados():
    return jsonify([e.to_dict() for e in EstadoExpediente.query.all()]), 200
