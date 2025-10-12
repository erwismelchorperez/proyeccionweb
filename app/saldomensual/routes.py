from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import SaldoMensualCTS, Template_Balance, CuentaContable, Periodo, Modelo, SucursalTemplate

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
    template = SucursalTemplate.query.filter_by(sucursalid=sucursalid, activo=True).first()
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
            saldo=monto,
            sucursalid = sucursalid
        )
        db.session.add(nuevo_saldo)

        registros_insertados.append({
            "codigo": codigo,
            "cuentaid": cuenta.cuentaid,
            "nombre": cuenta.nombre,
            "periodoid": periodo.periodoid,
            "sucursalid" : sucursalid,
            "saldo": float(monto)
        })

    db.session.commit()

    return jsonify({
        "message": "Saldos cargados exitosamente",
        "templateid": template.templateid,
        "periodoid": periodo.periodoid,
        "registros": registros_insertados
    }), 201
@saldo_mensual_cts_bp.route('/api/saldos/ultimo', methods=['POST'])
def api_obtener_ultimo_saldo():
    data = request.get_json()

    # Validar datos mínimos
    if not data or not all(k in data for k in ("institutionid", "sucursalid")):
        return jsonify({"error": "institutionid y sucursalid son requeridos"}), 400

    institutionid = data["institutionid"]
    sucursalid    = data["sucursalid"]

    # 1 Template activo de la sucursal
    template = Template_Balance.query.filter_by(sucursalid=sucursalid, activo=True).first()
    if not template:
        return jsonify({"error": "No existe template activo para esta sucursal"}), 400

    # 2 Último periodo con saldos registrados
    ultimo_periodo = (
        db.session.query(Periodo)
        .join(SaldoMensualCTS, SaldoMensualCTS.periodoid == Periodo.periodoid)
        .join(CuentaContable, CuentaContable.cuentaid == SaldoMensualCTS.cuentaid)
        .filter(CuentaContable.templateid == template.templateid,
                SaldoMensualCTS.sucursalid == sucursalid)  
        .order_by(Periodo.anio.desc(), Periodo.mes.desc())
        .first()
    )

    if not ultimo_periodo:
        return jsonify({"error": "No se encontraron saldos registrados para esta sucursal"}), 404

    # 3 Traer saldos y cuentas del último periodo
    saldos = (
        db.session.query(SaldoMensualCTS, CuentaContable)
        .join(CuentaContable, CuentaContable.cuentaid == SaldoMensualCTS.cuentaid)
        .filter(
            CuentaContable.templateid == template.templateid,
            SaldoMensualCTS.periodoid == ultimo_periodo.periodoid,
            SaldoMensualCTS.sucursalid == sucursalid)
        .all()
    )

    registros = []
    for saldo, cuenta in saldos:
        # Buscar los modelos relacionados con esta cuenta (relación 1:N)
        modelos = (
            Modelo.query
            .filter_by(cuentaid=cuenta.cuentaid, sucursalid=sucursalid)
            .all()
        )

        modelos_data = [
            {
                "modeloid": m.modeloid,
                "modelo": m.modelo,
                "ubicacion": m.ubicacion
            }
            for m in modelos
        ]

        registros.append({
            "codigo": cuenta.codigo,
            "nombre": cuenta.nombre,
            "saldo": float(saldo.saldo),
            "cuentaid": cuenta.cuentaid,
            "modelos": modelos_data
        })

    return jsonify({
        "message": "Último periodo con saldos encontrado",
        "institutionid": institutionid,
        "sucursalid": sucursalid,
        "templateid": template.templateid,
        "periodoid": ultimo_periodo.periodoid,
        "anio": ultimo_periodo.anio,
        "mes": ultimo_periodo.mes,
        "saldos": registros
    }), 200