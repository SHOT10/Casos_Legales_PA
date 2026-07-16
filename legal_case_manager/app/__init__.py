"""
Sistema de Gestión de Casos Legales (SGCL)
-------------------------------------------
Application factory. Crea y configura la instancia de Flask,
inicializa la base de datos (SQLAlchemy como conector) y registra
los blueprints que exponen la API REST.
"""
import os
from flask import Flask, jsonify
from .extensions import db
from .config import Config


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # --- Registro de blueprints (rutas de la API) -----------------------
    from .routes.auth import auth_bp
    from .routes.usuarios import usuarios_bp
    from .routes.aseguradoras import aseguradoras_bp
    from .routes.juzgados import juzgados_bp
    from .routes.expedientes import expedientes_bp
    from .routes.agenda import agenda_bp
    from .routes.dashboard import dashboard_bp
    from .routes.catalogos import catalogos_bp
    from .routes.web import web_bp

    app.register_blueprint(auth_bp,         url_prefix="/api/auth")
    app.register_blueprint(usuarios_bp,     url_prefix="/api/usuarios")
    app.register_blueprint(aseguradoras_bp, url_prefix="/api/aseguradoras")
    app.register_blueprint(juzgados_bp,     url_prefix="/api/juzgados")
    app.register_blueprint(expedientes_bp,  url_prefix="/api/expedientes")
    app.register_blueprint(agenda_bp,       url_prefix="/api/agenda")
    app.register_blueprint(dashboard_bp,    url_prefix="/api/dashboard")
    app.register_blueprint(catalogos_bp,    url_prefix="/api/catalogos")
    app.register_blueprint(web_bp)  # páginas HTML de la interfaz gráfica

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", service="SGCL API"), 200

    # --- Manejadores de error uniformes (respuestas JSON) ---------------
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify(error="Recurso no encontrado"), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=str(e.description) if hasattr(e, "description") else "Solicitud inválida"), 400

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify(error="Error interno del servidor"), 500

    with app.app_context():
        db.create_all()
        _seed_catalogos()

    return app


def _seed_catalogos():
    """Inserta catálogos base (roles / estados) si la BD está vacía."""
    from .models import Rol, EstadoExpediente

    if Rol.query.count() == 0:
        db.session.add_all([
            Rol(nombre="Administrador", descripcion="Acceso total al sistema"),
            Rol(nombre="Abogado", descripcion="Gestiona expedientes asignados"),
            Rol(nombre="Asistente", descripcion="Consulta y agenda"),
        ])
    if EstadoExpediente.query.count() == 0:
        db.session.add_all([
            EstadoExpediente(nombre="Pendiente"),
            EstadoExpediente(nombre="En curso"),
            EstadoExpediente(nombre="Cerrado"),
        ])
    db.session.commit()
