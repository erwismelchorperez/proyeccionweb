from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Variable, Pais, Template_Balance, TempVar

variables_bp = Blueprint('variable_bp', __name__)

@variables_bp.route('/api/variables/create', methods=['POST'])
def crear_variables():
    """
    Crea varias variables asociadas opcionalmente a un template.
    Si se pasa templateid, universo=False y se crea relación en TempVar.
    """
    data = request.get_json()

    templateid = data.get("templateid")
    variables_list = data.get("variables")

    if not variables_list or not isinstance(variables_list, list):
        return jsonify({"error": "Se espera una lista de variables en la clave 'variables'"}), 400

    # Validar template si se pasó
    if templateid:
        template = Template_Balance.query.get(templateid)
        if not template:
            return jsonify({"error": f"Template con id {templateid} no existe"}), 404
        universo = False
    else:
        universo = True

    errores = []
    objetos = []

    for idx, item in enumerate(variables_list, start=1):
        nombre = (item.get("nombrevariable") or "").strip()
        clavepais = item.get("clavepais")
        descripcion = item.get("descripcionvariable")

        # Validaciones
        if not nombre:
            errores.append(f"Fila {idx}: 'nombrevariable' es requerido")
            continue
        if not clavepais:
            errores.append(f"Fila {idx}: 'clavepais' es requerido")
            continue
        pais = Pais.query.get(clavepais)
        if not pais:
            errores.append(f"Fila {idx}: País con clave '{clavepais}' no existe")
            continue
        # Duplicado
        if Variable.query.filter_by(nombrevariable=nombre, clavepais=clavepais).first():
            errores.append(f"Fila {idx}: La variable '{nombre}' ya existe para el país '{clavepais}'")
            continue

        variable = Variable(
            nombrevariable=nombre,
            descripcionvariable=descripcion,
            clavepais=clavepais,
            universo=universo
        )
        objetos.append(variable)

    if errores:
        return jsonify({"message": "Validación fallida. No se insertó ninguna variable.", "errores": errores}), 400

    try:
        for variable in objetos:
            db.session.add(variable)
        db.session.flush()  # para obtener IDs

        # Crear relación TempVar si aplica
        if templateid:
            for variable in objetos:
                temp_var = TempVar(
                    variableid=variable.variableid,
                    templateid=templateid
                )
                db.session.add(temp_var)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al insertar en la base de datos", "details": str(e)}), 500

    return jsonify({
        "message": f"{len(objetos)} variables insertadas correctamente",
        "inserted": [
            {
                "variableid": v.variableid,
                "nombrevariable": v.nombrevariable,
                "descripcionvariable": v.descripcionvariable,
                "clavepais": v.clavepais,
                "universo": v.universo,
                "templateid": templateid if templateid else None
            } for v in objetos
        ]
    }), 201
@variables_bp.route('/api/variables/list', methods=['POST'])
def listar_variables():
    data = request.json or {}
    variableid = data.get('variableid')
    clavepais = data.get('clavepais')
    templateid = data.get('templateid')

    # --- 1️⃣ Caso: variable específica por ID ---
    if variableid:
        variable = Variable.query.get(variableid)
        if not variable:
            return jsonify({"error": f"No se encontró la variable con id {variableid}"}), 404

        result = {
            "variableid": variable.variableid,
            "nombrevariable": variable.nombrevariable,
            "descripcionvariable": variable.descripcionvariable,
            "clavepais": variable.clavepais,
            "universo": variable.universo
        }
        return jsonify(result), 200

    # --- 2️⃣ Caso: filtrar por templateid ---
    if templateid:
        # Obtener todas las variables ligadas a ese template
        variables_query = (
            db.session.query(Variable, TempVar)
            .join(TempVar, TempVar.variableid == Variable.variableid)
            .filter(TempVar.templateid == templateid)
        ).all()

        if not variables_query:
            return jsonify({"message": f"No se encontraron variables para el templateid '{templateid}'"}), 404

        # Construir la lista de variables
        variables_list = [
            {
                "variableid": v.Variable.variableid,
                "nombrevariable": v.Variable.nombrevariable,
                "descripcionvariable": v.Variable.descripcionvariable,
                "clavepais": v.Variable.clavepais,
                "universo": v.Variable.universo
            } for v in variables_query
        ]

        result = [{
            "templateid": templateid,
            "variables": variables_list
        }]
        return jsonify(result), 200

    # --- 3️⃣ Caso: filtrar por país (solo universo=True) ---
    if clavepais:
        variables = Variable.query.filter_by(clavepais=clavepais, universo=True).all()
        if not variables:
            return jsonify({"message": f"No se encontraron variables para clavepais '{clavepais}'"}), 404

    # --- 4️⃣ Caso: devolver todas ---
    else:
        variables = Variable.query.all()

    # Construir resultado genérico
    result = [
        {
            "variableid": v.variableid,
            "nombrevariable": v.nombrevariable,
            "descripcionvariable": v.descripcionvariable,
            "clavepais": v.clavepais,
            "universo": v.universo
        } for v in variables
    ]

    return jsonify(result), 200
