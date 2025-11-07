from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Indicador, Semaforo, Template_Balance

semaforo_bp = Blueprint('semaforo_bp', __name__)
@semaforo_bp.route('/api/semaforo/create', methods=['POST'])
def create_semaforo():
    data = request.json

    required_fields = ['indicadorid', 'templateid', 'nombre', 'condiciones']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Faltan campos requeridos: {', '.join(missing)}"}), 400

    indicador = Indicador.query.get(data['indicadorid'])
    if not indicador:
        return jsonify({"error": "El indicador no existe"}), 404

    template = Template_Balance.query.get(data['templateid'])
    if not template:
        return jsonify({"error": "El template no existe"}), 404

    condiciones = data['condiciones']
    if not isinstance(condiciones, list) or len(condiciones) == 0:
        return jsonify({"error": "El campo 'condiciones' debe ser una lista con al menos un elemento"}), 400
    if len(condiciones) > 6:
        return jsonify({"error": "Solo se permiten hasta 6 condiciones"}), 400

    # Evitar duplicado por indicador y template
    existente = Semaforo.query.filter_by(
        indicadorid=data['indicadorid'],
        templateid=data['templateid']
    ).first()

    if existente:
        return jsonify({"error": "Ya existe un semáforo para este indicador y template"}), 400

    semaforo = Semaforo(
        indicadorid=data['indicadorid'],
        templateid=data['templateid'],
        nombre=data['nombre'],
        condiciones=condiciones,
        limiteinf=data.get('limiteinferior'),
        limitesup=data.get('limitesuperior')
    )

    db.session.add(semaforo)
    db.session.commit()

    return jsonify({
        "semaforoid": semaforo.semaforoid,
        "indicadorid": semaforo.indicadorid,
        "templateid": semaforo.templateid,
        "nombre": semaforo.nombre,
        "condiciones": semaforo.condiciones
    }), 201
@semaforo_bp.route('/api/semaforo/listar', methods=['POST'])
def listar_semaforos():
    data = request.json or {}

    indicadorid = data.get("indicadorid")
    templateid = data.get("templateid")

    # ✅ Validar que al menos uno venga
    if not indicadorid and not templateid:
        return jsonify({"error": "Se requiere 'indicadorid' o 'templateid'"}), 400

    # 🔹 Si se envía templateid, filtramos por él
    if templateid:
        semaforos = Semaforo.query.filter_by(templateid=templateid).all()
        if not semaforos:
            return jsonify({"message": f"No hay semáforos registrados para el templateid {templateid}"}), 404

    # 🔹 Si no se envía templateid, filtramos por indicadorid
    elif indicadorid:
        indicador = Indicador.query.get(indicadorid)
        if not indicador:
            return jsonify({"error": f"No se encontró el indicador con id {indicadorid}"}), 404

        semaforos = Semaforo.query.filter_by(indicadorid=indicadorid).all()
        if not semaforos:
            return jsonify({"message": f"No hay semáforos registrados para el indicadorid {indicadorid}"}), 404

    # ✅ Construir respuesta
    result = [
        {
            "semaforoid": s.semaforoid,
            "indicadorid": s.indicadorid,
            "templateid": s.templateid,
            "nombre": s.nombre,
            "condiciones": s.condiciones,
            "limiteinferior": s.limiteinf,
            "limitesuperior": s.limitesup
        } for s in semaforos
    ]

    return jsonify(result), 200
@semaforo_bp.route('/api/semaforo/update', methods=['POST'])
def update_semaforo():
    data = request.json

    if not data or 'semaforoid' not in data:
        return jsonify({"error": "Se requiere el campo 'semaforoid'"}), 400

    semaforo = Semaforo.query.get(data['semaforoid'])
    if not semaforo:
        return jsonify({"error": "No se encontró el semáforo con el ID especificado"}), 404

    # ✅ Validar templateid si viene
    templateid = data.get('templateid')
    if templateid:
        template = Template_Balance.query.get(templateid)
        if not template:
            return jsonify({"error": f"No existe el template con ID {templateid}"}), 404

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
    semaforo.templateid = templateid or semaforo.templateid  # 👈 NUEVO

    db.session.commit()

    return jsonify({
        "message": "Semáforo actualizado correctamente",
        "semaforoid": semaforo.semaforoid,
        "nombre": semaforo.nombre,
        "templateid": semaforo.templateid,
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
