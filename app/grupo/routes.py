from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Grupo


grupo_bp = Blueprint('grupo_bp', __name__)

# Crear un nuevo grupo
@grupo_bp.route('/api/grupo/create', methods=['POST'])
def crear_grupo():
    data = request.get_json()
    nombre = data.get('nombre')

    if not nombre:
        return jsonify({"error": "El nombre del grupo es requerido"}), 400

    # Validar si ya existe
    if Grupo.query.filter_by(nombre=nombre).first():
        return jsonify({"error": "El grupo ya existe"}), 409

    grupo = Grupo(nombre=nombre)
    db.session.add(grupo)
    db.session.commit()

    return jsonify({
        "message": "Grupo creado exitosamente",
        "grupoid": grupo.grupoid,
        "nombre": grupo.nombre
    }), 201

# Listar todos los grupos
@grupo_bp.route('/api/grupo/list', methods=['GET'])
def listar_grupos():
    grupos = Grupo.query.all()
    return jsonify([
        {
            "grupoid": g.grupoid,
            "nombre": g.nombre
        } for g in grupos
    ])