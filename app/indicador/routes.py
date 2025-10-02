from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Grupo, Indicador, Pais

indicador_bp = Blueprint('indicador_bp', __name__)

# Crear indicador
@indicador_bp.route('/api/indicador/create', methods=['POST'])
def crear_indicador():
    data = request.get_json()

    grupoid = data.get('grupoid')
    clavepais = data.get('clavepais')
    indicador_nombre = data.get('indicador')
    descripcion = data.get('descripcion')
    formula = data.get('formula')  # Espera JSON

    if not grupoid or not indicador_nombre:
        return jsonify({"error": "grupoid e indicador son requeridos"}), 400

    # Validar existencia de grupo
    if not Grupo.query.get(grupoid):
        return jsonify({"error": "Grupo no existe"}), 404

    # Validar clavepais opcional
    if clavepais and not Pais.query.get(clavepais):
        return jsonify({"error": "País no existe"}), 404

    # Validar si ya existe el indicador
    indicador_existente = Indicador.query.filter_by(
        grupoid=grupoid,
        clavepais=clavepais,
        indicador=indicador_nombre
    ).first()

    if indicador_existente:
        return jsonify({"error": "El indicador ya existe para este grupo y país"}), 409

    # Crear nuevo indicador
    indicador = Indicador(
        grupoid=grupoid,
        clavepais=clavepais,
        indicador=indicador_nombre,
        descripcion=descripcion,
        formula=formula
    )
    db.session.add(indicador)
    db.session.commit()

    return jsonify({
        "message": "Indicador creado exitosamente",
        "indicadorid": indicador.indicadorid,
        "grupoid": indicador.grupoid,
        "clavepais": indicador.clavepais,
        "indicador": indicador.indicador
    }), 201
# Listar indicadores
@indicador_bp.route('/api/indicador/list', methods=['POST'])
def listar_indicadores():
    data = request.json or {}
    indicadorid = data.get('indicadorid')

    if indicadorid:
        indicador = Indicador.query.get(indicadorid)
        if not indicador:
            return jsonify({"error": f"No se encontró el indicador con id {indicadorid}"}), 404
        # Retorna un solo objeto
        result = {
            "indicadorid": indicador.indicadorid,
            "grupoid": indicador.grupoid,
            "clavepais": indicador.clavepais,
            "indicador": indicador.indicador,
            "descripcion": indicador.descripcion,
            "formula": indicador.formula
        }
        return jsonify(result), 200

    else:
        # Retorna todos
        indicadores = Indicador.query.all()
        result = [
            {
                "indicadorid": i.indicadorid,
                "grupoid": i.grupoid,
                "clavepais": i.clavepais,
                "indicador": i.indicador,
                "descripcion": i.descripcion,
                "formula": i.formula
            } for i in indicadores
        ]
        return jsonify(result), 200