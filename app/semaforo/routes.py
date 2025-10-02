from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Indicador, Semaforo

semaforo_bp = Blueprint('semaforo_bp', __name__)

@semaforo_bp.route('/api/semaforo/create', methods=['POST'])
def create_semaforo():
    data = request.json

    # Validar que el JSON trae lo necesario
    required_fields = ['indicadorid', 'nombre', 'color', 'operador1', 'valor1']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Faltan campos requeridos: {', '.join(missing)}"}), 400

    # Verificar que el indicador existe
    indicador = Indicador.query.get(data['indicadorid'])
    if not indicador:
        return jsonify({"error": "El indicador no existe"}), 404

    # Crear semaforo
    semaforo = Semaforo(
        indicadorid=data['indicadorid'],
        nombre=data['nombre'],
        color=data['color'],
        operador1=data['operador1'],
        valor1=data['valor1'],
        operador2=data.get('operador2'),
        valor2=data.get('valor2')
    )
    db.session.add(semaforo)
    db.session.commit()
    # Devolver el objeto recién creado en JSON
    return jsonify({
        "id": semaforo.semaforoid,
        "indicadorid": semaforo.indicadorid,
        "nombre": semaforo.nombre,
        "color": semaforo.color,
        "operador1": semaforo.operador1,
        "valor1": float(semaforo.valor1),
        "operador2": semaforo.operador2,
        "valor2": float(semaforo.valor2) if semaforo.valor2 else None
    }), 201
# Listar semaforos de un indicador (se pasa en JSON)
@semaforo_bp.route('/api/semaforo/listar', methods=['POST'])
def semaforolist():
    data = request.json

    if not data or 'indicadorid' not in data:
        return jsonify({"error": "Se requiere el campo 'indicadorid'"}), 400

    indicador = Indicador.query.get(data['indicadorid'])
    if not indicador:
        return jsonify({"error": "El indicador no existe"}), 404

    semaforos = Semaforo.query.filter_by(indicadorid=data['indicadorid']).all()
    return jsonify([
        {
            "id": semaforo.semaforoid,
            "nombre": semaforo.nombre,
            "color": semaforo.color,
            "operador1": semaforo.operador1,
            "valor1": float(semaforo.valor1),
            "operador2": semaforo.operador2,
            "valor2": float(semaforo.valor2) if semaforo.valor2 else None
        } for semaforo in semaforos
    ])