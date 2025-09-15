from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Variable, Template_Balance, TempVar

tempvar_bp = Blueprint('tempvar_bp', __name__)
@tempvar_bp.route('/api/tempvar/create', methods=['POST'])
def crear_tempvar():
    data = request.get_json()
    templateid = data.get("templateid")
    variableid = data.get("variableid")

    if not templateid or not variableid:
        return jsonify({"error": "templateid y variableid son requeridos"}), 400

    # Validar existencia de template y variable
    if not Template_Balance.query.get(templateid):
        return jsonify({"error": "Template no existe"}), 404
    if not Variable.query.get(variableid):
        return jsonify({"error": "Variable no existe"}), 404

    # ✅ Verificar si la relación ya existe
    existente = TempVar.query.filter_by(
        templateid=templateid,
        variableid=variableid
    ).first()
    if existente:
        return jsonify({"error": "La relación ya existe"}), 409  # 409 Conflict

    # Insertar relación
    registro = TempVar(templateid=templateid, variableid=variableid)
    db.session.add(registro)
    db.session.commit()

    return jsonify({
        "message": "Relación template-variable creada",
        "templateid": registro.templateid,
        "variableid": registro.variableid
    }), 201
@tempvar_bp.route('/api/tempvar/list', methods=['POST'])
def listar_tempvar():
    """
    Body JSON opcional:
    {
      "templateid": 1,
      "variableid": 5
    }
    """
    data = request.get_json(silent=True) or {}
    query = TempVar.query

    if "templateid" in data:
        query = query.filter_by(templateid=data["templateid"])
    if "variableid" in data:
        query = query.filter_by(variableid=data["variableid"])

    registros = query.all()
    return jsonify([
        {
            "templateid": r.templateid,
            "variableid": r.variableid
        }
        for r in registros
    ])