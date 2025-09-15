from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Variable, Pais

variables_bp = Blueprint('variable_bp', __name__)

@variables_bp.route('/api/crearvariables', methods=['POST'])
def crear_variables():
    """
    Inserta varias variables en una sola operación.
    Si algún elemento falla, no se inserta ninguno.
    """
    data = request.get_json()

    # Debe venir {"variables":[...]}
    if not isinstance(data, dict) or "variables" not in data:
        return jsonify({"error": "Se espera un objeto con la clave 'variables' que contenga una lista"}), 400

    variables_list = data["variables"]
    if not isinstance(variables_list, list) or not variables_list:
        return jsonify({"error": "La clave 'variables' debe ser una lista no vacía"}), 400

    errores = []
    objetos = []

    # === Validar todos antes de insertar ===
    for idx, item in enumerate(variables_list, start=1):
        nombre = (item.get("nombrevariable") or "").strip()
        clavepais = item.get("clavepais")

        if not nombre:
            errores.append(f"Fila {idx}: 'nombrevariable' es requerido")
            continue
        if not clavepais:
            errores.append(f"Fila {idx}: 'clavepais' es requerido")
            continue

        # Verificar que el país exista
        pais = Pais.query.get(clavepais)
        if not pais:
            errores.append(f"Fila {idx}: País con clave '{clavepais}' no existe")
            continue

        # Preparar objeto si todo bien
        objetos.append(
            Variable(
                nombrevariable=nombre,
                descripcionvariable=item.get("descripcionvariable"),
                clavepais=clavepais
            )
        )

    # Si hay algún error, abortar la operación
    if errores:
        return jsonify({
            "message": "Validación fallida. No se insertó ninguna variable.",
            "errores": errores
        }), 400

    # === Insertar todo en una sola transacción ===
    try:
        for obj in objetos:
            db.session.add(obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Error al insertar en la base de datos",
            "details": str(e)
        }), 500

    return jsonify({
        "message": f"{len(objetos)} variables insertadas correctamente",
        "inserted": [
            {
                "variableid": v.variableid,
                "nombrevariable": v.nombrevariable,
                "descripcionvariable": v.descripcionvariable,
                "clavepais": v.clavepais
            } for v in objetos
        ]
    }), 201
@variables_bp.route('/api/listvariables', methods=['POST'])
def listar_variables():
    data = request.get_json(silent=True) or {}
    clavepais = data.get("clavepais")

    # Si envían clave, filtrar; si no, traer todos
    if clavepais:
        variables = Variable.query.filter_by(clavepais=clavepais).all()
    else:
        variables = Variable.query.all()

    return jsonify([
        {
            "variableid": v.variableid,
            "nombrevariable": v.nombrevariable,
            "descripcionvariable": v.descripcionvariable,
            "clavepais": v.clavepais
        } for v in variables
    ])