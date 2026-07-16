"""
Pruebas de la API REST del Sistema de Gestión de Casos Legales.
Ejecutar con:  pytest -v
"""
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.config import Config
from app.extensions import db
from app.models import Rol, Aseguradora, Juzgado, EstadoExpediente
from app.auth_utils import hash_password
from app.models import Usuario


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        rol = Rol.query.filter_by(nombre="Administrador").first()
        db.session.add(Usuario(
            nombre_completo="Usuario Prueba",
            usuario="test",
            correo="test@test.com",
            password_hash=hash_password("Password123"),
            id_rol=rol.id_rol,
        ))
        db.session.add(Aseguradora(nombre="ASEGURADORA TEST"))
        db.session.add(Juzgado(nombre="JUZGADO TEST"))
        db.session.commit()
    with app.test_client() as c:
        yield c


def _token(client):
    r = client.post("/api/auth/login", json={"usuario": "test", "password": "Password123"})
    return r.get_json()["token"]


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_login_correcto(client):
    r = client.post("/api/auth/login", json={"usuario": "test", "password": "Password123"})
    assert r.status_code == 200
    assert "token" in r.get_json()


def test_login_incorrecto(client):
    r = client.post("/api/auth/login", json={"usuario": "test", "password": "incorrecta"})
    assert r.status_code == 401


def test_acceso_sin_token_es_rechazado(client):
    r = client.get("/api/expedientes")
    assert r.status_code == 401


def test_crear_y_listar_expediente(client):
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/expedientes", headers=headers, json={
        "numero_expediente": "EXP-TEST-001",
        "asegurado_nombre": "PERSONA DE PRUEBA",
        "id_aseguradora": 1,
        "id_juzgado": 1,
        "id_estado": 1,
    })
    assert r.status_code == 201
    assert r.get_json()["numero_expediente"] == "EXP-TEST-001"

    r = client.get("/api/expedientes", headers=headers)
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_no_permite_numero_expediente_duplicado(client):
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "numero_expediente": "EXP-DUP-001",
        "asegurado_nombre": "PERSONA X",
        "id_aseguradora": 1,
        "id_juzgado": 1,
        "id_estado": 1,
    }
    r1 = client.post("/api/expedientes", headers=headers, json=payload)
    r2 = client.post("/api/expedientes", headers=headers, json=payload)
    assert r1.status_code == 201
    assert r2.status_code == 409


def test_filtro_por_estado(client):
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/expedientes", headers=headers, json={
        "numero_expediente": "EXP-EST-001", "asegurado_nombre": "A",
        "id_aseguradora": 1, "id_juzgado": 1, "id_estado": 1,
    })
    client.post("/api/expedientes", headers=headers, json={
        "numero_expediente": "EXP-EST-002", "asegurado_nombre": "B",
        "id_aseguradora": 1, "id_juzgado": 1, "id_estado": 3,
    })
    r = client.get("/api/expedientes?estado=Cerrado", headers=headers)
    data = r.get_json()
    assert len(data) == 1
    assert data[0]["numero_expediente"] == "EXP-EST-002"


def test_dashboard_contadores(client):
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/expedientes", headers=headers, json={
        "numero_expediente": "EXP-DASH-001", "asegurado_nombre": "A",
        "id_aseguradora": 1, "id_juzgado": 1, "id_estado": 1,
    })
    r = client.get("/api/dashboard", headers=headers)
    assert r.status_code == 200
    assert r.get_json()["contadores"]["Pendiente"] == 1
