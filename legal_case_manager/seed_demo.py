"""
Carga datos de ejemplo para poder probar la API rápidamente,
replicando el tipo de información mostrada en el prototipo
(aseguradoras, juzgados y expedientes de muestra).

Uso:
    python seed_demo.py
"""
from datetime import date
from app import create_app
from app.extensions import db
from app.models import Usuario, Rol, Aseguradora, Juzgado, EstadoExpediente, Expediente, Agenda
from app.auth_utils import hash_password

app = create_app()

with app.app_context():
    admin_rol = Rol.query.filter_by(nombre="Administrador").first()

    if not Usuario.query.filter_by(usuario="jperez").first():
        db.session.add(Usuario(
            nombre_completo="Lic. Juan Pérez",
            usuario="jperez",
            correo="jperez@ejemplo.com",
            password_hash=hash_password("Password123"),
            id_rol=admin_rol.id_rol,
        ))

    aseguradoras = ["ASSA", "ANCON", "AIISA", "CONANCO", "PARTICULAR", "INTEROCEANICA"]
    for nombre in aseguradoras:
        if not Aseguradora.query.filter_by(nombre=nombre).first():
            db.session.add(Aseguradora(nombre=nombre))

    juzgados = [
        "JUZGADO 5TO (PEDREGAL)", "JUZGADO 4TO (PEDREGAL)", "JUZGADO 3RO (PEDREGAL)",
        "JUZGADO 1RO (PEDREGAL)", "ALCALDÍA DE PANAMÁ", "JUZGADO DE CHITRÉ",
    ]
    for nombre in juzgados:
        if not Juzgado.query.filter_by(nombre=nombre).first():
            db.session.add(Juzgado(nombre=nombre))

    db.session.commit()

    estado_pendiente = EstadoExpediente.query.filter_by(nombre="Pendiente").first()
    estado_curso = EstadoExpediente.query.filter_by(nombre="En curso").first()
    estado_cerrado = EstadoExpediente.query.filter_by(nombre="Cerrado").first()
    assa = Aseguradora.query.filter_by(nombre="ASSA").first()
    ancon = Aseguradora.query.filter_by(nombre="ANCON").first()
    juzgado5 = Juzgado.query.filter_by(nombre="JUZGADO 5TO (PEDREGAL)").first()
    juzgado4 = Juzgado.query.filter_by(nombre="JUZGADO 4TO (PEDREGAL)").first()
    usuario = Usuario.query.filter_by(usuario="jperez").first()

    demo_expedientes = [
        ("EXP-2019-001", "ANTHONY TREJOS", assa, juzgado5, estado_pendiente),
        ("EXP-2019-002", "LUIS MOLINA", ancon, juzgado4, estado_curso),
        ("EXP-2019-003", "KATHERINE KENT", assa, juzgado5, estado_cerrado),
    ]
    for numero, nombre_asegurado, aseguradora, juzgado, estado in demo_expedientes:
        if not Expediente.query.filter_by(numero_expediente=numero).first():
            exp = Expediente(
                numero_expediente=numero,
                asegurado_nombre=nombre_asegurado,
                id_aseguradora=aseguradora.id_aseguradora,
                id_juzgado=juzgado.id_juzgado,
                id_estado=estado.id_estado,
                id_usuario_asignado=usuario.id_usuario,
            )
            db.session.add(exp)

    db.session.commit()

    primer_exp = Expediente.query.first()
    if primer_exp and Agenda.query.count() == 0:
        db.session.add(Agenda(
            id_expediente=primer_exp.id_expediente,
            titulo="Audiencia preliminar",
            descripcion="Presentación de pruebas",
            fecha_evento=date.today(),
            completado=False,
        ))
        db.session.commit()

    print("Datos de demostración cargados correctamente.")
    print("Usuario de prueba -> usuario: jperez | password: Password123")
