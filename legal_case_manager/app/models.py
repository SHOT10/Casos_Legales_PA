from datetime import datetime, date
from .extensions import db


class Rol(db.Model):
    __tablename__ = "roles"
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))

    usuarios = db.relationship("Usuario", backref="rol", lazy=True)

    def to_dict(self):
        return {"id_rol": self.id_rol, "nombre": self.nombre, "descripcion": self.descripcion}


class Usuario(db.Model):
    __tablename__ = "usuarios"
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(120), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    correo = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey("roles.id_rol"), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre_completo": self.nombre_completo,
            "usuario": self.usuario,
            "correo": self.correo,
            "rol": self.rol.nombre if self.rol else None,
            "activo": self.activo,
        }


class Aseguradora(db.Model):
    __tablename__ = "aseguradoras"
    id_aseguradora = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(30))
    correo = db.Column(db.String(120))
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "id_aseguradora": self.id_aseguradora,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "correo": self.correo,
            "activo": self.activo,
        }


class Juzgado(db.Model):
    __tablename__ = "juzgados"
    id_juzgado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)
    circuito = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "id_juzgado": self.id_juzgado,
            "nombre": self.nombre,
            "circuito": self.circuito,
            "activo": self.activo,
        }


class EstadoExpediente(db.Model):
    __tablename__ = "estados_expediente"
    id_estado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), unique=True, nullable=False)

    def to_dict(self):
        return {"id_estado": self.id_estado, "nombre": self.nombre}


class Expediente(db.Model):
    __tablename__ = "expedientes"
    id_expediente = db.Column(db.Integer, primary_key=True)
    numero_expediente = db.Column(db.String(50), unique=True, nullable=False)
    asegurado_nombre = db.Column(db.String(150), nullable=False)
    id_aseguradora = db.Column(db.Integer, db.ForeignKey("aseguradoras.id_aseguradora"), nullable=False)
    id_juzgado = db.Column(db.Integer, db.ForeignKey("juzgados.id_juzgado"), nullable=False)
    id_estado = db.Column(db.Integer, db.ForeignKey("estados_expediente.id_estado"), nullable=False)
    id_usuario_asignado = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"))
    descripcion = db.Column(db.Text)
    fecha_apertura = db.Column(db.Date, default=date.today)
    fecha_cierre = db.Column(db.Date)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, onupdate=datetime.utcnow)

    aseguradora = db.relationship("Aseguradora")
    juzgado = db.relationship("Juzgado")
    estado = db.relationship("EstadoExpediente")
    usuario_asignado = db.relationship("Usuario")
    eventos = db.relationship("Agenda", backref="expediente", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id_expediente": self.id_expediente,
            "numero_expediente": self.numero_expediente,
            "asegurado_nombre": self.asegurado_nombre,
            "aseguradora": self.aseguradora.nombre if self.aseguradora else None,
            "juzgado": self.juzgado.nombre if self.juzgado else None,
            "estado": self.estado.nombre if self.estado else None,
            "usuario_asignado": self.usuario_asignado.nombre_completo if self.usuario_asignado else None,
            "descripcion": self.descripcion,
            "fecha_apertura": self.fecha_apertura.isoformat() if self.fecha_apertura else None,
            "fecha_cierre": self.fecha_cierre.isoformat() if self.fecha_cierre else None,
        }


class Agenda(db.Model):
    __tablename__ = "agenda"
    id_evento = db.Column(db.Integer, primary_key=True)
    id_expediente = db.Column(db.Integer, db.ForeignKey("expedientes.id_expediente"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_evento = db.Column(db.Date, nullable=False)
    hora_evento = db.Column(db.Time)
    completado = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id_evento": self.id_evento,
            "id_expediente": self.id_expediente,
            "numero_expediente": self.expediente.numero_expediente if self.expediente else None,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "fecha_evento": self.fecha_evento.isoformat() if self.fecha_evento else None,
            "hora_evento": self.hora_evento.isoformat() if self.hora_evento else None,
            "completado": self.completado,
        }
