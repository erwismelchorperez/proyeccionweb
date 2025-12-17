from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import CuentaContable, Modelo, Template_Balance

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
def api_obtener_modelos_por_template():
    data = request.get_json(silent=True) or {}

    if not all(k in data for k in ("templateid", "sucursalid")):
        return jsonify({
            "error": "templateid y sucursalid son requeridos"
        }), 400

    templateid = int(data["templateid"])
    sucursalid = int(data["sucursalid"])

    # 1️⃣ Validar template
    template = Template_Balance.query.filter_by(templateid=templateid).first()
    if not template:
        return jsonify({
            "error": "El template no existe"
        }), 404

    # 2️⃣ Query principal (equivalente al SELECT)
    resultados = (
        db.session.query(
            Template_Balance.templateid,
            CuentaContable.cuentaid,
            CuentaContable.codigo,
            CuentaContable.nombre,
            Modelo.modeloid,
            Modelo.modelo,
            Modelo.ubicacion
        )
        .join(CuentaContable, CuentaContable.templateid == Template_Balance.templateid)
        .join(Modelo, Modelo.cuentaid == CuentaContable.cuentaid)
        .filter(
            Template_Balance.templateid == templateid,
            Modelo.sucursalid == sucursalid
        )
        .order_by(CuentaContable.codigo.asc())
        .all()
    )

    if not resultados:
        return jsonify({
            "error": "No existen modelos registrados para este template y sucursal"
        }), 404

    # 3️⃣ Formatear respuesta
    data_respuesta = []
    for r in resultados:
        data_respuesta.append({
            "cuentaid": r.cuentaid,
            "codigo": r.codigo,
            "nombre": r.nombre,
            "modeloid": r.modeloid,
            "modelo": r.modelo,
            "ubicacion": r.ubicacion
        })

    return jsonify({
        "message": "Modelos encontrados",
        "templateid": templateid,
        "sucursalid": sucursalid,
        "total": len(data_respuesta),
        "data": data_respuesta
    }), 200
