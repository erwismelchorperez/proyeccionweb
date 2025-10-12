from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import ValorIndicador, Indicador, Periodo

valorindicador_bp = Blueprint('valorindicador_bp', __name__)

# Crear valor de indicador
@valorindicador_bp.route('/api/valorindicador/create', methods=['POST'])
def crear_valorindicador():
    """
    Body JSON:
    {
        "indicadorid": 1,
        "periodoid": 5,
        "valor": 123.45
    }
    """
    data = request.get_json()
    indicadorid = data.get("indicadorid")
    periodoid = data.get("periodoid")
    valor = data.get("valor")
    sucursalid = data.get("sucursalid")

    if not indicadorid or not periodoid:
        return jsonify({"error": "indicadorid y periodoid son requeridos"}), 400

    # Validar existencia de indicador y periodo
    if not Indicador.query.get(indicadorid):
        return jsonify({"error": "Indicador no existe"}), 404
    if not Periodo.query.get(periodoid):
        return jsonify({"error": "Periodo no existe"}), 404

    # Validar que no exista duplicado
    existing = ValorIndicador.query.filter_by(indicadorid=indicadorid, periodoid=periodoid).first()
    if existing:
        return jsonify({"error": "Valor ya registrado para este indicador y periodo"}), 400

    # Crear registro
    registro = ValorIndicador(indicadorid=indicadorid, periodoid=periodoid, valor=valor, sucursalid = sucursalid)
    db.session.add(registro)
    db.session.commit()

    return jsonify({
        "message": "Valor de indicador creado",
        "valorindid": registro.valorindid,
        "indicadorid": registro.indicadorid,
        "periodoid": registro.periodoid,
        "valor": float(registro.valor),
        "sucursalid":registro.sucursalid
    }), 201

# Listar valores (opcional filtro por indicador o periodo)
@valorindicador_bp.route('/api/valorindicador/list', methods=['POST'])
def listar_valorindicador():
    """
    Body JSON opcional:
    {
        "indicadorid": 1,
        "periodoid": 5
    }
    """
    data = request.get_json() or {}
    indicadorid = data.get("indicadorid")
    periodoid = data.get("periodoid")

    query = ValorIndicador.query
    if indicadorid:
        query = query.filter_by(indicadorid=indicadorid)
    if periodoid:
        query = query.filter_by(periodoid=periodoid)

    registros = query.all()
    return jsonify([
        {
            "valorindid": r.valorindid,
            "indicadorid": r.indicadorid,
            "periodoid": r.periodoid,
            "valor": float(r.valor),
            "sucursalid": r.sucursalid
        } for r in registros
    ])
# listar valor de los indicadores por sucursal