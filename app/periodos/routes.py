from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Periodo

periodo_bp = Blueprint('periodo', __name__, template_folder='templates')
@periodo_bp.route('/api/CreatePeriodos', methods=['POST'])
def api_create_periodos():
    data = request.get_json()

    # Validación de entrada
    if not data or "periodos" not in data:
        return jsonify({"error": "Se requiere un arreglo 'periodos'"}), 400

    periodos = data["periodos"]
    if not isinstance(periodos, list) or len(periodos) == 0:
        return jsonify({"error": "'periodos' debe ser una lista con al menos un elemento"}), 400

    registros_insertados = []
    for p in periodos:
        anio = p.get("anio")
        mes = p.get("mes")

        # Validar campos
        if anio is None or mes is None:
            return jsonify({"error": "Cada periodo debe incluir 'anio' y 'mes'"}), 400

        # Verificar que no exista ya
        if Periodo.query.filter_by(anio=anio, mes=mes).first():
            # Omitimos duplicados para no romper la carga
            continue

        nuevo = Periodo(anio=anio, mes=mes)
        db.session.add(nuevo)
        registros_insertados.append({"anio": anio, "mes": mes})

    db.session.commit()

    return jsonify({
        "message": "Periodos creados correctamente",
        "registros_insertados": registros_insertados
    }), 201
@periodo_bp.route('/api/ListPeriodos', methods=['POST'])
def api_list_periodos_post():
    data = request.get_json() or {}
    anio = data.get("anio")
    mes = data.get("mes")

    query = Periodo.query
    if anio:
        query = query.filter_by(anio=anio)
    if mes:
        query = query.filter_by(mes=mes)

    periodos = query.order_by(Periodo.anio, Periodo.mes).all()

    return jsonify([
        {
            "periodoid": p.periodoid,
            "anio": p.anio,
            "mes": p.mes
        } for p in periodos
    ])
@periodo_bp.route('/api/ListPeriodosPorAnio', methods=['POST'])
def listar_periodos_por_anio_post():
    """
    Body JSON opcional:
    {
        "anios": [2024, 2025]  # si se omite, devuelve todos los años
    }
    """
    data = request.get_json() or {}
    anios_filtro = data.get("anios", None)

    query = Periodo.query
    if anios_filtro:
        query = query.filter(Periodo.anio.in_(anios_filtro))

    periodos = query.order_by(Periodo.anio, Periodo.mes).all()

    resultado = {}
    for p in periodos:
        if p.anio not in resultado:
            resultado[p.anio] = []
        resultado[p.anio].append(p.mes)

    return jsonify(resultado)