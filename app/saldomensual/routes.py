from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import SaldoMensualCTS, Template_Balance, CuentaContable, Periodo

saldo_mensual_cts_bp = Blueprint('saldo_mensual_cts_bp', __name__)

@saldo_mensual_cts_bp.route('/api/Createsaldos', methods=['POST'])
def api_crear_saldos():
    data = request.get_json()

    # Validar campos mínimos
    if not data or not all(k in data for k in ("institutionid", "sucursalid", "anio", "mes", "saldos")):
        return jsonify({"error": "institutionid, sucursalid, anio, mes y saldos son requeridos"}), 400

    sucursalid = data["sucursalid"]
    anio       = data["anio"]
    mes        = data["mes"]
    saldos     = data["saldos"]

    # 1️⃣ Verificar que el periodo exista
    periodo = Periodo.query.filter_by(anio=anio, mes=mes).first()
    if not periodo:
        return jsonify({"error": f"No existe un periodo registrado para {anio}-{mes}"}), 400

    # 2️⃣ Template activo de la sucursal
    template = Template_Balance.query.filter_by(sucursalid=sucursalid, activo=True).first()
    if not template:
        return jsonify({"error": "No existe template activo para esta sucursal"}), 400

    # 3️⃣ Cuentas válidas del template
    cuentas = CuentaContable.query.filter_by(templateid=template.templateid).all()
    cuentas_dict = {c.codigo: c for c in cuentas}
    if not cuentas_dict:
        return jsonify({"error": "El template activo no tiene cuentas contables"}), 400

    registros_insertados = []

    # 4️⃣ Procesar cada saldo
    for item in saldos:
        codigo = item.get("codigo")
        nombre = item.get("nombre")
        monto  = item.get("saldo")

        if not codigo or monto is None:
            return jsonify({"error": "Cada saldo debe incluir 'codigo' y 'saldo'"}), 400

        cuenta = cuentas_dict.get(codigo)
        if not cuenta:
            return jsonify({"error": f"La cuenta con código {codigo} no pertenece al template activo"}), 400

        # Validar nombre opcional
        if nombre and cuenta.nombre != nombre:
            return jsonify({"error": f"El nombre '{nombre}' no coincide con la cuenta '{cuenta.nombre}'"}), 400

        # ✅ Insertar usando el ID del periodo
        nuevo_saldo = SaldoMensualCTS(
            cuentaid=cuenta.cuentaid,
            periodoid=periodo.periodoid,   # <<-- aquí
            saldo=monto
        )
        db.session.add(nuevo_saldo)

        registros_insertados.append({
            "codigo": codigo,
            "cuentaid": cuenta.cuentaid,
            "nombre": cuenta.nombre,
            "periodoid": periodo.periodoid,
            "saldo": float(monto)
        })

    db.session.commit()

    return jsonify({
        "message": "Saldos cargados exitosamente",
        "templateid": template.templateid,
        "periodoid": periodo.periodoid,
        "registros": registros_insertados
    }), 201
