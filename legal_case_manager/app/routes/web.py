from flask import Blueprint, render_template, redirect

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def index():
    return redirect("/dashboard")


@web_bp.get("/login")
def login_page():
    return render_template("login.html")


@web_bp.get("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@web_bp.get("/expedientes")
def expedientes_page():
    return render_template("expedientes.html")


@web_bp.get("/agenda")
def agenda_page():
    return render_template("agenda.html")


@web_bp.get("/catalogos")
def catalogos_page():
    return render_template("catalogos.html")
