from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import CuentaContable, Modelo

modelos_bp = Blueprint('modelos_bp', __name__)

@modelos_bp.route('/api/modelos/create', methods=['POST'])
def crear_modelo():
    data = request.get_json()
    
    cuentaid = data.get('cuentaid')
    modelo_nombre = data.get('modelo')
    ubicacion = data.get('ubicacion')

    if not cuentaid:
        return jsonify({"error": "cuentaid es requerido"}), 400

    # Validar que la cuenta exista
    cuenta = CuentaContable.query.get(cuentaid)
    if not cuenta:
        return jsonify({"error": "Cuenta contable no existe"}), 404

    nuevo_modelo = Modelo(cuentaid=cuentaid, modelo=modelo_nombre, ubicacion=ubicacion)
    db.session.add(nuevo_modelo)
    db.session.commit()

    return jsonify({
        "message": "Modelo creado exitosamente",
        "modeloid": nuevo_modelo.modeloid,
        "cuentaid": nuevo_modelo.cuentaid,
        "modelo": nuevo_modelo.modelo,
        "ubicacion": nuevo_modelo.ubicacion
    }), 201
@modelos_bp.route('/api/modelos/list', methods=['POST'])
def listar_modelos():
    data = request.get_json() or {}
    cuentaid = data.get('cuentaid')

    query = Modelo.query
    if cuentaid:
        query = query.filter_by(cuentaid=cuentaid)

    modelos = query.all()
    return jsonify([
        {
            "modeloid": m.modeloid,
            "cuentaid": m.cuentaid,
            "modelo": m.modelo,
            "ubicacion": m.ubicacion
        } for m in modelos
    ])