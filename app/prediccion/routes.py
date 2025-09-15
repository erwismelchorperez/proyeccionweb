from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Prediccion, Modelo, SucursalTemplate, CuentaContable

predicciones_bp = Blueprint('predicciones_bp', __name__)

@predicciones_bp.route('/api/predicciones/create', methods=['POST'])
def crear_prediccion():
    data = request.get_json()

    modeloid = data.get('modeloid')
    periodoid = data.get('periodoid')
    valor = data.get('prediccion')

    if not modeloid or not periodoid:
        return jsonify({"error": "modeloid y periodoid son requeridos"}), 400

    # Validar existencia del modelo y periodo
    modelo = Modelo.query.get(modeloid)
    if not modelo:
        return jsonify({"error": "Modelo no existe"}), 404

    # Aquí puedes validar si el periodoid existe, dependiendo de tu tabla periodo
    # periodo = Periodo.query.get(periodoid)
    # if not periodo:
    #     return jsonify({"error": "Periodo no existe"}), 404

    prediccion = Prediccion(modeloid=modeloid, periodoid=periodoid, prediccion=valor)
    db.session.add(prediccion)
    db.session.commit()

    return jsonify({
        "message": "Predicción creada exitosamente",
        "prediccionid": prediccion.prediccionid,
        "modeloid": prediccion.modeloid,
        "periodoid": prediccion.periodoid,
        "prediccion": str(prediccion.prediccion)
    }), 201
@predicciones_bp.route('/api/predicciones/list', methods=['POST'])
def listar_predicciones():
    data = request.get_json() or {}
    modeloid = data.get('modeloid')
    periodoid = data.get('periodoid')

    query = Prediccion.query
    if modeloid:
        query = query.filter_by(modeloid=modeloid)
    if periodoid:
        query = query.filter_by(periodoid=periodoid)

    predicciones = query.all()
    return jsonify([
        {
            "prediccionid": p.prediccionid,
            "modeloid": p.modeloid,
            "periodoid": p.periodoid,
            "prediccion": str(p.prediccion)
        } for p in predicciones
    ])
@predicciones_bp.route('/api/predicciones/sucursal', methods=['POST'])
def predicciones_por_sucursal():
    """
    Body JSON:
    {
        "sucursalid": 1
    }
    """
    data = request.get_json()
    sucursalid = data.get("sucursalid")
    if not sucursalid:
        return jsonify({"error": "sucursalid es requerido"}), 400

    # Obtener templates activos de la sucursal
    templates_activos = db.session.query(SucursalTemplate.templateid).filter_by(sucursalid=sucursalid, activo=True).subquery()

    # Cuentas contables de esos templates
    cuentas = db.session.query(CuentaContable.cuentaid).filter(CuentaContable.templateid.in_(templates_activos)).subquery()

    # Obtener los Modelos asociados a esas cuentas contables
    modelos = db.session.query(Modelo.modeloid).filter(Modelo.cuentaid.in_(cuentas)).subquery()

    # Obtener predicciones de esos modelos
    predicciones = Prediccion.query.filter(Prediccion.modeloid.in_(modelos)).all()

    resultado = [
        {
            "prediccionid": p.prediccionid,
            "modeloid": p.modeloid,
            "periodoid": p.periodoid,
            "valor": float(p.prediccion)
        } for p in predicciones
    ]

    return jsonify(resultado)