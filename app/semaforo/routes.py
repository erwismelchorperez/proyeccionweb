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

    # ✅ Validar campos principales
    required_fields = ['indicadorid', 'nombre', 'condiciones']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Faltan campos requeridos: {', '.join(missing)}"}), 400

    # ✅ Verificar que el indicador existe
    indicador = Indicador.query.get(data['indicadorid'])
    if not indicador:
        return jsonify({"error": "El indicador no existe"}), 404

    # ✅ Validar estructura de condiciones
    condiciones = data['condiciones']
    if not isinstance(condiciones, list) or len(condiciones) == 0:
        return jsonify({"error": "El campo 'condiciones' debe ser una lista con al menos un elemento"}), 400

    # 🚫 Limitar máximo 6 condiciones
    if len(condiciones) > 6:
        return jsonify({"error": "Solo se permiten hasta 6 condiciones por semáforo"}), 400

    for i, c in enumerate(condiciones):
        if not all(k in c for k in ('rangomin', 'rangomax', 'operadores', 'color')):
            return jsonify({"error": f"Faltan campos en condición {i+1}. Se requiere 'rangomin', 'rangomax', 'operadores' y 'color'"}), 400
        
        if len(c['operadores']) != 2:
            return jsonify({"error": f"La condición {i+1} debe tener exactamente 2 operadores"}), 400

    # ✅ Crear nuevo registro de semáforo
    semaforo = Semaforo(
        indicadorid=data['indicadorid'],
        nombre=data['nombre'],
        condiciones=condiciones,  # 👈 guardamos como JSON
        limiteinf=data.get('limiteinferior'),
        limitesup=data.get('limitesuperior')
    )

    db.session.add(semaforo)
    db.session.commit()

    # ✅ Respuesta
    return jsonify({
        "semaforoid": semaforo.semaforoid,
        "indicadorid": semaforo.indicadorid,
        "nombre": semaforo.nombre,
        "condiciones": semaforo.condiciones,
        "limiteinferior": semaforo.limiteinf,
        "limitesuperior": semaforo.limitesup
    }), 201
# 📌 Listar semáforos de un indicador
@semaforo_bp.route('/api/semaforo/listar', methods=['POST'])
def listar_semaforos():
    data = request.json

    if not data or 'indicadorid' not in data:
        return jsonify({"error": "Se requiere el campo 'indicadorid'"}), 400

    indicador = Indicador.query.get(data['indicadorid'])
    if not indicador:
        return jsonify({"error": "El indicador no existe"}), 404

    semaforos = Semaforo.query.filter_by(indicadorid=data['indicadorid']).all()

    if not semaforos:
        return jsonify({"message": "No hay semáforos registrados para este indicador"}), 404

    return jsonify([
        {
            "semaforoid": s.semaforoid,
            "indicadorid": s.indicadorid,
            "nombre": s.nombre,
            "condiciones": s.condiciones,
            "limiteinferior": s.limiteinf,
            "limitesuperior": s.limitesup
        } for s in semaforos
    ]), 200
@semaforo_bp.route('/api/semaforo/update', methods=['POST'])
def update_semaforo():
    data = request.json

    if not data or 'semaforoid' not in data:
        return jsonify({"error": "Se requiere el campo 'semaforoid'"}), 400

    semaforo = Semaforo.query.get(data['semaforoid'])
    if not semaforo:
        return jsonify({"error": "No se encontró el semáforo con el ID especificado"}), 404

    # ✅ Validar condiciones si vienen
    condiciones = data.get('condiciones')
    if condiciones:
        if not isinstance(condiciones, list):
            return jsonify({"error": "El campo 'condiciones' debe ser una lista"}), 400
        if len(condiciones) > 6:
            return jsonify({"error": "Solo se permiten hasta 6 condiciones por semáforo"}), 400

        # ✅ Validación de estructura de cada condición
        for i, c in enumerate(condiciones):
            if not all(k in c for k in ('rangomin', 'rangomax', 'operadores', 'color')):
                return jsonify({
                    "error": f"Faltan campos en condición {i+1}. "
                             f"Se requiere 'rangomin', 'rangomax', 'operadores' y 'color'"
                }), 400

            if len(c['operadores']) != 2:
                return jsonify({
                    "error": f"La condición {i+1} debe tener exactamente 2 operadores"
                }), 400

    # ✅ Actualizar campos
    semaforo.nombre = data.get('nombre', semaforo.nombre)
    semaforo.condiciones = condiciones or semaforo.condiciones
    semaforo.limiteinf = data.get('limiteinferior', semaforo.limiteinf)
    semaforo.limitesup = data.get('limitesuperior', semaforo.limitesup)

    db.session.commit()

    return jsonify({
        "message": "Semáforo actualizado correctamente",
        "semaforoid": semaforo.semaforoid,
        "nombre": semaforo.nombre,
        "condiciones": semaforo.condiciones,
        "limiteinferior": semaforo.limiteinf,
        "limitesuperior": semaforo.limitesup
    }), 200
@semaforo_bp.route('/api/semaforo/delete', methods=['DELETE'])
def delete_semaforo():
    data = request.json

    if not data or 'semaforoid' not in data:
        return jsonify({"error": "Se requiere el campo 'semaforoid'"}), 400

    semaforo = Semaforo.query.get(data['semaforoid'])
    if not semaforo:
        return jsonify({"error": "No se encontró el semáforo con el ID especificado"}), 404

    db.session.delete(semaforo)
    db.session.commit()

    return jsonify({"message": f"Semáforo con ID {data['semaforoid']} eliminado correctamente"}), 200
