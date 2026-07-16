import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-secreta-para-el-taller-cambiar-en-produccion")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'sgcl.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXP_MINUTES = 60 * 8  # 8 horas de sesión
