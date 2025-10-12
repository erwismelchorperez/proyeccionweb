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
    variables = data.get('variables')  # <-- aquí capturamos el JSON
    sucursalid = data.get('sucursalid')

    if not cuentaid:
        return jsonify({"error": "cuentaid es requerido"}), 400

    # Validar que la cuenta exista
    cuenta = CuentaContable.query.get(cuentaid)
    if not cuenta:
        return jsonify({"error": "Cuenta contable no existe"}), 404
    
    # Validar que variables (si viene) sea dict o list
    if variables is not None and not isinstance(variables, (dict, list)):
        return jsonify({
            "error": "El campo 'variables' debe ser un objeto JSON o una lista de objetos"
        }), 400

    nuevo_modelo = Modelo(cuentaid=cuentaid, modelo=modelo_nombre, ubicacion=ubicacion, variables= variables, sucursalid = sucursalid)
    db.session.add(nuevo_modelo)
    db.session.commit()

    return jsonify({
        "message": "Modelo creado exitosamente",
        "modeloid": nuevo_modelo.modeloid,
        "cuentaid": nuevo_modelo.cuentaid,
        "modelo": nuevo_modelo.modelo,
        "ubicacion": nuevo_modelo.ubicacion,
        "variables": variables,
        "sucursalid": nuevo_modelo.sucursalid
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
            "ubicacion": m.ubicacion,
            "variables":m.variables
        } for m in modelos
    ])
# listas todos los modelos por sucursal