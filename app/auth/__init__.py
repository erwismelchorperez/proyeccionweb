from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

from . import routes  # <- Muy importante para que se registren las rutas
