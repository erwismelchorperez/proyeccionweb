from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import CuentaContable, TipoCuenta

cuentacontable_bp = Blueprint('cuentacontable_bp', __name__)

@cuentacontable_bp.route('/api/CreateCuentas', methods=['POST'])
def api_crear_cuentas():
    data = request.get_json()

    if not data or "templateid" not in data or "cuentas" not in data:
        return jsonify({"error": "templateid y arreglo de cuentas son requeridos"}), 400

    templateid = data["templateid"]
    cuentas = data["cuentas"]

    # ---------------------------
    # 1️⃣ Validar todos los datos
    # ---------------------------
    errores = []
    cuentas_validadas = []

    for idx, c in enumerate(cuentas, start=1):
        clave_tipo = c.get("tipocuenta")
        if not clave_tipo:
            errores.append(f"Cuenta {idx}: falta la clave 'tipocuenta'")
            continue

        tipo = TipoCuenta.query.filter_by(clavetipo=clave_tipo).first()
        if not tipo:
            errores.append(f"Cuenta {idx}: tipo de cuenta '{clave_tipo}' no existe")
            continue

        # Guardar los datos validados en memoria
        cuentas_validadas.append({
            "nivel": c.get("nivel"),
            "tipoid": tipo.tipocuentaid,
            "codigo": c.get("codigo"),
            "nombre": c.get("nombre"),
            "proyeccion": c.get("proyeccion"),
            "segmento": c.get("segmento")
        })

    # Si hay errores, no se inserta nada
    if errores:
        return jsonify({
            "error": "Validación fallida. No se insertó ninguna cuenta.",
            "detalles": errores
        }), 400
    print(cuentas_validadas)
    # ---------------------------
    # 2️⃣ Insertar en una sola transacción
    # ---------------------------
    nuevas_cuentas = []
    for c in cuentas_validadas:
        cuenta = CuentaContable(
            templateid=templateid,
            nivel=c["nivel"],
            tipoid=c["tipoid"],
            codigo=c["codigo"],
            nombre=c["nombre"],
            proyeccion=c["proyeccion"],
            segmento=c["segmento"]
        )
        db.session.add(cuenta)
        nuevas_cuentas.append(cuenta)

    db.session.commit()

    return jsonify({
        "message": "Todas las cuentas fueron creadas exitosamente",
        "cuentas": [
            {
                "cuentaid": c.cuentaid,
                "templateid": c.templateid,
                "codigo": c.codigo,
                "nombre": c.nombre,
                "tipoid": c.tipoid
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
    cuenta.tipoid = data.get("tipo", cuenta.tipoid)
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
            "tipoid": c.tipoid,
            "codigo": c.codigo,
            "nombre": c.nombre,
            "proyeccion": c.proyeccion,
            "segmento": c.segmento
        }
        for c in cuentas
    ])

