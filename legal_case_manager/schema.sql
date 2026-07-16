-- =====================================================================
-- Esquema de Base de Datos
-- Sistema de Gestión de Casos Legales (SGCL)
-- Motor: SQLite (compatible con PostgreSQL/MySQL con ajustes menores)
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- Tabla: roles
-- Catálogo de roles de usuario dentro del sistema
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id_rol      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      VARCHAR(50) NOT NULL UNIQUE,      -- Ej: Administrador, Abogado, Asistente
    descripcion VARCHAR(255)
);

-- ---------------------------------------------------------------------
-- Tabla: usuarios
-- Usuarios que acceden al sistema (login del prototipo)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo VARCHAR(120) NOT NULL,
    usuario         VARCHAR(50)  NOT NULL UNIQUE,   -- login
    correo          VARCHAR(120) UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    id_rol          INTEGER NOT NULL,
    activo          BOOLEAN NOT NULL DEFAULT 1,
    creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- ---------------------------------------------------------------------
-- Tabla: aseguradoras
-- Catálogo de aseguradoras (columna "Aseguradora" en el prototipo)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS aseguradoras (
    id_aseguradora INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         VARCHAR(120) NOT NULL UNIQUE,
    telefono       VARCHAR(30),
    correo         VARCHAR(120),
    activo         BOOLEAN NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------------
-- Tabla: juzgados
-- Catálogo de juzgados / tribunales
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS juzgados (
    id_juzgado INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre     VARCHAR(150) NOT NULL UNIQUE,   -- Ej: JUZGADO 5TO (PEDREGAL)
    circuito   VARCHAR(100),
    activo     BOOLEAN NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------------
-- Tabla: estados_expediente
-- Catálogo de estados posibles de un expediente
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estados_expediente (
    id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    VARCHAR(30) NOT NULL UNIQUE   -- Pendiente, En curso, Cerrado
);

-- ---------------------------------------------------------------------
-- Tabla: expedientes
-- Tabla central: representa cada caso/expediente legal
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expedientes (
    id_expediente     INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_expediente VARCHAR(50) NOT NULL UNIQUE,
    asegurado_nombre  VARCHAR(150) NOT NULL,       -- Ej: ANTHONY TREJOS
    id_aseguradora    INTEGER NOT NULL,
    id_juzgado        INTEGER NOT NULL,
    id_estado         INTEGER NOT NULL,
    id_usuario_asignado INTEGER,                   -- abogado responsable
    descripcion       TEXT,
    fecha_apertura    DATE NOT NULL DEFAULT (DATE('now')),
    fecha_cierre      DATE,
    creado_en         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en    DATETIME,
    FOREIGN KEY (id_aseguradora)      REFERENCES aseguradoras(id_aseguradora),
    FOREIGN KEY (id_juzgado)          REFERENCES juzgados(id_juzgado),
    FOREIGN KEY (id_estado)           REFERENCES estados_expediente(id_estado),
    FOREIGN KEY (id_usuario_asignado) REFERENCES usuarios(id_usuario)
);

-- ---------------------------------------------------------------------
-- Tabla: agenda
-- Eventos/audiencias asociados a un expediente ("Agenda del día")
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agenda (
    id_evento     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_expediente INTEGER NOT NULL,
    titulo        VARCHAR(150) NOT NULL,
    descripcion   TEXT,
    fecha_evento  DATE NOT NULL,
    hora_evento   TIME,
    completado    BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (id_expediente) REFERENCES expedientes(id_expediente)
);

-- ---------------------------------------------------------------------
-- Índices para optimizar las consultas más frecuentes de la API
-- ---------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_expedientes_estado     ON expedientes(id_estado);
CREATE INDEX IF NOT EXISTS idx_expedientes_aseguradora ON expedientes(id_aseguradora);
CREATE INDEX IF NOT EXISTS idx_expedientes_juzgado     ON expedientes(id_juzgado);
CREATE INDEX IF NOT EXISTS idx_agenda_fecha            ON agenda(fecha_evento);

-- ---------------------------------------------------------------------
-- Datos semilla mínimos (catálogos)
-- ---------------------------------------------------------------------
INSERT OR IGNORE INTO roles (nombre, descripcion) VALUES
    ('Administrador', 'Acceso total al sistema'),
    ('Abogado', 'Gestiona expedientes asignados'),
    ('Asistente', 'Consulta y agenda');

INSERT OR IGNORE INTO estados_expediente (nombre) VALUES
    ('Pendiente'), ('En curso'), ('Cerrado');
