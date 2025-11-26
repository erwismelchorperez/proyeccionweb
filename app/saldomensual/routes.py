from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models import SaldoMensualCTS, Template_Balance, CuentaContable, Periodo, Modelo, SucursalTemplate, InstitutionTemplate

saldo_mensual_cts_bp = Blueprint('saldo_mensual_cts_bp', __name__)

@saldo_mensual_cts_bp.route('/api/saldos/Createsaldos', methods=['POST', 'GET'])
def api_crear_saldos():

    # Si es GET devolvemos un mensaje o datos
    if request.method == 'GET':
        return jsonify({
            "message": "Endpoint activo. Usa POST para enviar saldos."
        }), 200

    # POST
    try:
        data = request.get_json(silent=True) or {}

        requeridos = ("institutionid", "sucursalid", "anio", "mes", "saldos")
        faltantes = [k for k in requeridos if k not in data]
        if faltantes:
            return jsonify({"error": f"Faltan campos: {', '.join(faltantes)}"}), 400

        institutionid = int(data["institutionid"])
        sucursalid    = int(data["sucursalid"])
        anio          = int(data["anio"])

        # mes puede venir como entero o dict
        mes = data["mes"]
        if isinstance(mes, dict):
            mes = int(mes.get("mes"))
        else:
            mes = int(mes)
        if not (1 <= mes <= 12):
            return jsonify({"error": "mes debe estar en 1..12"}), 400

        saldos = data["saldos"]
        if not isinstance(saldos, list) or not saldos:
            return jsonify({"error": "saldos debe ser una lista no vacía"}), 400

        # 1) periodo
        periodo = Periodo.query.filter_by(anio=anio, mes=mes).first()
        if not periodo:
            # si NO quieres crearlo automáticamente, deja el 400
            return jsonify({"error": f"No existe un periodo registrado para {anio}-{mes}"}), 400
            # o hacer lo anterior manual:
            # periodo = Periodo(anio=anio, mes=mes)
            # db.session.add(periodo)
            # db.session.flush()

        # 2) template activo (elige un modelo consistente en todo el proyecto)
        template_rel = InstitutionTemplate.query.filter_by(institutionid=institutionid, activo=True).first()
        if not template_rel:
            return jsonify({"error": "No existe template activo para esta institución"}), 400

        # 3) cuentas válidas del template
        cuentas = CuentaContable.query.filter_by(templateid=template_rel.templateid).all()
        cuentas_por_codigo = {c.codigo: c for c in cuentas}
        if not cuentas_por_codigo:
            return jsonify({"error": "El template activo no tiene cuentas contables"}), 400

        # 4) construir filas para UPSERT
        filas = []
        registros_resumen = []
        for item in saldos:
            codigo = item.get("codigo")
            nombre = item.get("nombre")
            monto  = item.get("saldo")

            if not codigo or monto is None:
                return jsonify({"error": "Cada saldo debe incluir 'codigo' y 'saldo'"}), 400

            cuenta = cuentas_por_codigo.get(codigo)
            if not cuenta:
                return jsonify({"error": f"La cuenta con código {codigo} no pertenece al template activo"}), 400

            if nombre and cuenta.nombre != nombre:
                return jsonify({"error": f"El nombre '{nombre}' no coincide con la cuenta '{cuenta.nombre}'"}), 400

            filas.append({
                "cuentaid":   int(cuenta.cuentaid),
                "periodoid":  int(periodo.periodoid),
                "saldo":      monto,
                "sucursalid": int(sucursalid),
            })
            registros_resumen.append({
                "codigo": codigo,
                "cuentaid": cuenta.cuentaid,
                "nombre": cuenta.nombre,
                "periodoid": periodo.periodoid,
                "sucursalid": sucursalid,
                "saldo": float(monto)
            })

        if not filas:
            return jsonify({"error": "No hay filas válidas para insertar"}), 400

        # 5) UPSERT masivo (ON CONFLICT DO UPDATE)
        stmt = pg_insert(SaldoMensualCTS.__table__).values(filas)
        stmt = stmt.on_conflict_do_update(
            index_elements=["cuentaid", "periodoid"],  # debe coincidir con tu UNIQUE real
            set_={
                "saldo": stmt.excluded.saldo,
                "sucursalid": stmt.excluded.sucursalid,
            },
        )
        db.session.execute(stmt)
        db.session.commit()

        return jsonify({
            "message": "Saldos cargados/actualizados exitosamente",
            "templateid": template_rel.templateid,
            "periodoid": periodo.periodoid,
            "registros": registros_resumen,
            "upserted": len(filas)
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Integridad de datos", "detalle": str(e.orig)}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "DB error", "detalle": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno", "detalle": str(e)}), 500
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
@saldo_mensual_cts_bp.route('/api/saldos/all', methods=['POST'])
def api_obtener_todos_saldos():
    data = request.get_json()

    if not data or not all(k in data for k in ("institutionid", "sucursalid")):
        return jsonify({"error": "institutionid y sucursalid son requeridos"}), 400

    institutionid = data["institutionid"]
    sucursalid    = data["sucursalid"]

    # 1️⃣ Obtener template activo mediante institucion_balance
    relacion = InstitutionTemplate.query.filter_by(
        institutionid=institutionid,
        activo=True
    ).first()

    if not relacion:
        return jsonify({"error": "La institución no tiene template activo registrado"}), 400

    template = Template_Balance.query.filter_by(templateid=relacion.templateid).first()

    if not template:
        return jsonify({"error": "El template activo no existe"}), 400

    # 2️⃣ Buscar todos los periodos donde existan saldos de esa sucursal
    periodos = (
        db.session.query(Periodo)
        .join(SaldoMensualCTS, SaldoMensualCTS.periodoid == Periodo.periodoid)
        .join(CuentaContable, CuentaContable.cuentaid == SaldoMensualCTS.cuentaid)
        .filter(
            CuentaContable.templateid == template.templateid,
            SaldoMensualCTS.sucursalid == sucursalid
        )
        .order_by(Periodo.anio.desc(), Periodo.mes.desc())
        .all()
    )

    if not periodos:
        return jsonify({"error": "No existen saldos registrados para esta sucursal"}), 404

    respuesta_periodos = []

    # 3️⃣ Recorrer cada periodo y traer sus saldos
    for periodo in periodos:
        saldos = (
            db.session.query(SaldoMensualCTS, CuentaContable)
            .join(CuentaContable, CuentaContable.cuentaid == SaldoMensualCTS.cuentaid)
            .filter(
                CuentaContable.templateid == template.templateid,
                SaldoMensualCTS.periodoid == periodo.periodoid,
                SaldoMensualCTS.sucursalid == sucursalid
            )
            .all()
        )

        registros = []
        for saldo, cuenta in saldos:
            registros.append({
                "codigo": cuenta.codigo,
                "nombre": cuenta.nombre,
                "saldo": float(saldo.saldo),
                "cuentaid": cuenta.cuentaid
            })

        respuesta_periodos.append({
            "periodoid": periodo.periodoid,
            "anio": periodo.anio,
            "mes": periodo.mes,
            "saldos": registros
        })

    return jsonify({
        "message": "Listado de saldos por periodo",
        "institutionid": institutionid,
        "sucursalid": sucursalid,
        "templateid": template.templateid,
        "periodos": respuesta_periodos
    }), 200
@saldo_mensual_cts_bp.route('/api/saldos/periodos', methods=['POST'])
def api_obtener_periodos_por_anio():
    data = request.get_json()

    if not data or not all(k in data for k in ("institutionid", "sucursalid")):
        return jsonify({"error": "institutionid y sucursalid son requeridos"}), 400

    institutionid = data["institutionid"]
    sucursalid    = data["sucursalid"]

    # 1️⃣ Obtener template activo mediante institucion_balance
    relacion = InstitutionTemplate.query.filter_by(
        institutionid=institutionid,
        activo=True
    ).first()

    if not relacion:
        return jsonify({"error": "La institución no tiene template activo registrado"}), 400

    template = Template_Balance.query.filter_by(templateid=relacion.templateid).first()

    if not template:
        return jsonify({"error": "El template activo no existe"}), 400

    # 2️⃣ Obtener todos los periodos donde existan saldos para la sucursal
    periodos = (
        db.session.query(Periodo)
        .join(SaldoMensualCTS, SaldoMensualCTS.periodoid == Periodo.periodoid)
        .join(CuentaContable, CuentaContable.cuentaid == SaldoMensualCTS.cuentaid)
        .filter(
            CuentaContable.templateid == template.templateid,
            SaldoMensualCTS.sucursalid == sucursalid
        )
        .order_by(Periodo.anio.asc(), Periodo.mes.asc())
        .all()
    )

    if not periodos:
        return jsonify({"error": "No existen periodos registrados para esta sucursal"}), 404

    # 3️⃣ Agrupar por año
    periodos_por_anio = {}

    for p in periodos:
        anio = str(p.anio)

        if anio not in periodos_por_anio:
            periodos_por_anio[anio] = []

        # Evitar meses duplicados
        if p.mes not in periodos_por_anio[anio]:
            periodos_por_anio[anio].append(p.mes)

    return jsonify(periodos_por_anio), 200
@saldo_mensual_cts_bp.route('/api/saldos/periodos/template', methods=['POST'])
def api_obtener_periodos_por_template():
    data = request.get_json()

    # Validar campos recibidos
    for field in data.keys():
        if field not in {"templateid"}:
            return jsonify({"error": "templateid son requeridos"}), 400

    templateid = data["templateid"]

    # 1️⃣ Verificar la existencia del template
    template = Template_Balance.query.filter_by(templateid=templateid).first()
    if not template:
        return jsonify({"error": "El template no existe"}), 404

    # 2️⃣ Buscar periodos donde existan saldos relacionados a este template y sucursal
    periodos = (
        db.session.query(Periodo)
        .join(SaldoMensualCTS, SaldoMensualCTS.periodoid == Periodo.periodoid)
        .join(CuentaContable, CuentaContable.cuentaid == SaldoMensualCTS.cuentaid)
        .filter(
            CuentaContable.templateid == templateid
        )
        .order_by(Periodo.anio.asc(), Periodo.mes.asc())
        .all()
    )

    # Si no existen periodos → entonces el template NO tiene saldos
    if not periodos:
        return jsonify({
            "error": "El template no tiene saldos registrados",
            "templateid": templateid
        }), 404

    # 3️⃣ Agrupar meses por año
    periodos_por_anio = {}

    for p in periodos:
        anio = str(p.anio)

        if anio not in periodos_por_anio:
            periodos_por_anio[anio] = []

        if p.mes not in periodos_por_anio[anio]:
            periodos_por_anio[anio].append(p.mes)

    return jsonify({
        "templateid": templateid,
        "periodos": periodos_por_anio
    }), 200
@saldo_mensual_cts_bp.route('/api/saldos/aniomes', methods=['POST'])
def api_obtener_saldos_por_periodo():
    data = request.get_json()

    # Validación de campos requeridos
    campos_requeridos = ("institutionid", "sucursalid", "anio", "mes")
    if not data or not all(k in data for k in campos_requeridos):
        return jsonify({"error": "institutionid, sucursalid, anio y mes son requeridos"}), 400

    institutionid = data["institutionid"]
    sucursalid    = data["sucursalid"]
    anio          = data["anio"]
    mes           = data["mes"]

    # 1️⃣ Obtener template activo mediante institucion_balance
    relacion = InstitutionTemplate.query.filter_by(
        institutionid=institutionid,
        activo=True
    ).first()

    if not relacion:
        return jsonify({"error": "La institución no tiene template activo registrado"}), 400

    template = Template_Balance.query.filter_by(templateid=relacion.templateid).first()

    if not template:
        return jsonify({"error": "El template activo no existe"}), 400

    # 2️⃣ Buscar periodo específico
    periodo = Periodo.query.filter_by(anio=anio, mes=mes).first()

    if not periodo:
        return jsonify({"error": "El periodo especificado no existe"}), 404

    # 3️⃣ Buscar saldos para ese periodo, sucursal y template
    saldos = (
        db.session.query(SaldoMensualCTS, CuentaContable)
        .join(CuentaContable, CuentaContable.cuentaid == SaldoMensualCTS.cuentaid)
        .filter(
            CuentaContable.templateid == template.templateid,
            SaldoMensualCTS.periodoid == periodo.periodoid,
            SaldoMensualCTS.sucursalid == sucursalid
        )
        .all()
    )

    if not saldos:
        return jsonify({"error": "No existen saldos registrados para ese periodo y sucursal"}), 404

    registros = []
    for saldo, cuenta in saldos:
        registros.append({
            "codigo": cuenta.codigo,
            "nombre": cuenta.nombre,
            "saldo": float(saldo.saldo),
            "cuentaid": cuenta.cuentaid
        })

    return jsonify({
        "message": "Saldos del periodo solicitado",
        "institutionid": institutionid,
        "sucursalid": sucursalid,
        "templateid": template.templateid,
        "periodo": {
            "periodoid": periodo.periodoid,
            "anio": periodo.anio,
            "mes": periodo.mes,
            "saldos": registros
        }
    }), 200
