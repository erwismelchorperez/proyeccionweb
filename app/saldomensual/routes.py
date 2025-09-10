from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import SaldoMensualCTS, Template_Balance, CuentaContable

saldo_mensual_cts_bp = Blueprint('saldo_mensual_cts_bp', __name__)

@saldo_mensual_cts_bp.route('/api/Createsaldos', methods=['POST'])
def api_crear_saldos():
    data = request.get_json()

    # Validar entrada mínima
    if not data or "institutionid" not in data or "sucursalid" not in data or "saldos" not in data:
        return jsonify({"error": "institutionid, sucursalid y saldos son requeridos"}), 400

    institutionid = data["institutionid"]
    sucursalid = data["sucursalid"]
    saldos = data["saldos"]

    # 1. Buscar template activo de esa sucursal
    template = Template_Balance.query.filter_by(
        sucursalid=sucursalid,
        activo=True
    ).first()

    if not template:
        return jsonify({"error": "No existe template activo para esta sucursal"}), 400

    # 2. Obtener todas las cuentas de ese template
    cuentas_validas = {c.cuentaid for c in CuentaContable.query.filter_by(templateid=template.templateid).all()}

    if not cuentas_validas:
        return jsonify({"error": "El template activo no tiene cuentas contables"}), 400

    # 3. Insertar los saldos validados
    registros_insertados = []
    for saldo in saldos:
        cuentaid = saldo.get("cuentaid")
        anio = saldo.get("anio")
        mes = saldo.get("mes")
        monto = saldo.get("saldo")

        # Validación de cuenta existente dentro del template
        if cuentaid not in cuentas_validas:
            return jsonify({"error": f"La cuentaid {cuentaid} no pertenece al template activo"}), 400

        nuevo_saldo = SaldoMensualCTS(
            cuentaid=cuentaid,
            anio=anio,
            mes=mes,
            saldo=monto
        )
        db.session.add(nuevo_saldo)
        registros_insertados.append({
            "cuentaid": cuentaid,
            "anio": anio,
            "mes": mes,
            "saldo": monto
        })

    db.session.commit()

    return jsonify({
        "message": "Saldos cargados exitosamente",
        "templateid": template.templateid,
        "sucursalid": sucursalid,
        "registros": registros_insertados
    }), 201
