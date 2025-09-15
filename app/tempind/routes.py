from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Indicador, Template_Balance, TempInd


tempind_bp = Blueprint('tempind_bp', __name__)

# Crear relación indicador-variable
@tempind_bp.route('/api/tempind/create', methods=['POST'])
def crear_tempind():
    """
    Body JSON:
    {
        "indicadorid": 1,
        "templateid": 1
    }
    """
    data = request.get_json()
    indicadorid = data.get("indicadorid")
    templateid = data.get("templateid")

    if not indicadorid or not templateid:
        return jsonify({"error": "indicadorid y variableid son requeridos"}), 400

    # Validar existencia de indicador y variable
    if not Indicador.query.get(indicadorid):
        return jsonify({"error": "Indicador no existe"}), 404
    if not Template_Balance.query.get(templateid):
        return jsonify({"error": "Template no existe"}), 404

    # Validar que la relación no exista ya
    existing = TempInd.query.filter_by(indicadorid=indicadorid, templateid=templateid).first()
    if existing:
        return jsonify({"error": "La relación ya existe"}), 400

    # Crear registro
    registro = TempInd(indicadorid=indicadorid, templateid=templateid)
    db.session.add(registro)
    db.session.commit()

    return jsonify({
        "message": "Relación indicador-variable creada",
        "indicadorid": registro.indicadorid,
        "templateid": registro.templateid
    }), 201


# Listar todas las relaciones o filtrar por indicador
@tempind_bp.route('/api/tempind/list', methods=['POST'])
def listar_tempind():
    """
    Body JSON opcional:
    {
        "indicadorid": 1
    }
    """
    data = request.get_json() or {}
    indicadorid = data.get("indicadorid")

    query = TempInd.query
    if indicadorid:
        query = query.filter_by(indicadorid=indicadorid)

    registros = query.all()

    return jsonify([
        {
            "indicadorid": r.indicadorid,
            "templateid": r.templateid
        } for r in registros
    ])
