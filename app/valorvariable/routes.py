from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Variable, Periodo, ValorVariable

valorvariable_bp = Blueprint('valorvariable_bp', __name__)

@valorvariable_bp.route('/api/valorvariable/create', methods=['POST'])
def crear_valor_variable():
    """
    JSON esperado:
    {
      "abort_on_error": true,
      "valores": [
        {"variableid": 1, "periodoid": 5, "valor": 23.45},
        {"variableid": 2, "periodoid": 6, "valor": 10.10}
      ]
    }
    """
    data = request.get_json()
    if not data or "valores" not in data:
        return jsonify({"error": "El arreglo 'valores' es requerido"}), 400

    abort_on_error = bool(data.get("abort_on_error", False))
    valores = data["valores"]

    nuevos = []
    errores = []

    for idx, v in enumerate(valores, start=1):
        variableid = v.get("variableid")
        periodoid  = v.get("periodoid")
        valor      = v.get("valor")

        # Validar campos obligatorios
        if not variableid or not periodoid:
            errores.append(f"Registro {idx}: variableid y periodoid son obligatorios")
            continue

        # Validar existencia de variable y periodo
        if not Variable.query.get(variableid):
            errores.append(f"Registro {idx}: variableid {variableid} no existe")
            continue
        if not Periodo.query.get(periodoid):
            errores.append(f"Registro {idx}: periodoid {periodoid} no existe")
            continue

        nuevos.append(ValorVariable(
            variableid=variableid,
            periodoid=periodoid,
            valor=valor
        ))

    # Si modo todo/nada y hubo errores, cancelar
    if abort_on_error and errores:
        return jsonify({"error": "Validación fallida", "detalles": errores}), 400

    try:
        for n in nuevos:
            db.session.add(n)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Error al guardar", "detalle": str(e)}), 500

    return jsonify({
        "message": "Valores insertados",
        "insertados": [ {"valorvariableid": x.valorvariableid,
                         "variableid": x.variableid,
                         "periodoid": x.periodoid,
                         "valor": float(x.valor) if x.valor is not None else None}
                        for x in nuevos ],
        "errores": errores
    }), 201
@valorvariable_bp.route('/api/valorvariable/list', methods=['POST'])
def listar_valor_variable():
    """
    JSON opcional para filtrar:
    {
      "variableid": 1,
      "periodoid": 5
    }
    Si no se envía nada, retorna todos los registros.
    """
    data = request.get_json(silent=True) or {}
    variableid = data.get("variableid")
    periodoid  = data.get("periodoid")

    query = ValorVariable.query
    if variableid:
        query = query.filter_by(variableid=variableid)
    if periodoid:
        query = query.filter_by(periodoid=periodoid)

    registros = query.all()

    return jsonify([
        {
            "valorvariableid": r.valorvariableid,
            "variableid": r.variableid,
            "periodoid": r.periodoid,
            "valor": float(r.valor) if r.valor is not None else None
        }
        for r in registros
    ])