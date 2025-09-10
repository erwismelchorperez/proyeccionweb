from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import CuentaContable

cuentacontable_bp = Blueprint('cuentacontable_bp', __name__)

@cuentacontable_bp.route('/api/CreateCuentas', methods=['POST'])
def api_crear_cuentas():
    data = request.get_json()

    if not data or "templateid" not in data or "cuentas" not in data:
        return jsonify({"error": "templateid y arreglo de cuentas son requeridos"}), 400

    templateid = data["templateid"]
    cuentas = data["cuentas"]

    nuevas_cuentas = []
    for c in cuentas:
        cuenta = CuentaContable(
            templateid=templateid,
            nivel=c.get("nivel"),
            tipo=c.get("tipo"),
            codigo=c.get("codigo"),
            nombre=c.get("nombre"),
            proyeccion=c.get("proyeccion"),
            segmento=c.get("segmento")
        )
        db.session.add(cuenta)
        nuevas_cuentas.append(cuenta)

    db.session.commit()

    return jsonify({
        "message": "Cuentas creadas exitosamente",
        "cuentas": [
            {
                "cuentaid": c.cuentaid,
                "templateid": c.templateid,
                "codigo": c.codigo,
                "nombre": c.nombre
            } for c in nuevas_cuentas
        ]
    }), 201
@cuentacontable_bp.route('/api/UpdateCuenta', methods=['POST'])
def api_update_cuenta():
    data = request.get_json()

    if not data or "cuentaid" not in data:
        return jsonify({"error": "cuentaid es requerido"}), 400

    cuenta = CuentaContable.query.get(data["cuentaid"])
    if not cuenta:
        return jsonify({"error": "Cuenta no encontrada"}), 404

    # Actualizar campos
    cuenta.nivel = data.get("nivel", cuenta.nivel)
    cuenta.tipo = data.get("tipo", cuenta.tipo)
    cuenta.codigo = data.get("codigo", cuenta.codigo)
    cuenta.nombre = data.get("nombre", cuenta.nombre)
    cuenta.proyeccion = data.get("proyeccion", cuenta.proyeccion)
    cuenta.segmento = data.get("segmento", cuenta.segmento)

    db.session.commit()

    return jsonify({"message": "Cuenta actualizada exitosamente"})
@cuentacontable_bp.route('/api/ListCuentas', methods=['POST'])
def api_list_cuentas():
    data = request.get_json()

    if not data or "templateid" not in data:
        return jsonify({"error": "templateid es requerido"}), 400

    cuentas = CuentaContable.query.filter_by(templateid=data["templateid"]).all()

    return jsonify([
        {
            "cuentaid": c.cuentaid,
            "templateid": c.templateid,
            "nivel": c.nivel,
            "tipo": c.tipo,
            "codigo": c.codigo,
            "nombre": c.nombre,
            "proyeccion": c.proyeccion,
            "segmento": c.segmento
        }
        for c in cuentas
    ])

