from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import EscenarioCuenta
escenariocuenta_bp = Blueprint('escenariocuenta_bp', __name__)

# Crear relación
@escenariocuenta_bp.route('/api/escenariocuenta/create', methods=['POST'])
def create_escenariocuenta():
    data = request.get_json()

    # Se espera que llegue: {"cuentaid": 1, "escenarioid": 2}
    try:
        rel = EscenarioCuenta(
            cuentaid=data['cuentaid'],
            escenarioid=data['escenarioid']
        )
        db.session.add(rel)
        db.session.commit()
        return jsonify({"message": "Relación creada", "cuentaid": rel.cuentaid, "escenarioid": rel.escenarioid}), 201
    except KeyError as e:
        return jsonify({"error": f"Falta el campo: {str(e)}"}), 400


# Listar todas las relaciones
@escenariocuenta_bp.route('/api/escenariocuenta/list', methods=['POST'])
def list_escenariocuenta():
    relaciones = EscenarioCuenta.query.all()
    return jsonify([
        {"cuentaid": r.cuentaid, "escenarioid": r.escenarioid}
        for r in relaciones
    ])