from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Prediccion, Modelo, SucursalTemplate, CuentaContable, Periodo, SaldoMensualCTS

predicciones_bp = Blueprint('predicciones_bp', __name__)

@predicciones_bp.route('/api/predicciones/create', methods=['POST'])
def crear_prediccion():
    data = request.get_json()

    modeloid = data.get('modeloid')
    periodoid = data.get('periodoid')
    valor = data.get('prediccion')

    if not modeloid or not periodoid:
        return jsonify({"error": "modeloid y periodoid son requeridos"}), 400

    # Validar existencia del modelo y periodo
    modelo = Modelo.query.get(modeloid)
    if not modelo:
        return jsonify({"error": "Modelo no existe"}), 404

    # Aquí puedes validar si el periodoid existe, dependiendo de tu tabla periodo
    # periodo = Periodo.query.get(periodoid)
    # if not periodo:
    #     return jsonify({"error": "Periodo no existe"}), 404

    prediccion = Prediccion(modeloid=modeloid, periodoid=periodoid, prediccion=valor)
    db.session.add(prediccion)
    db.session.commit()

    return jsonify({
        "message": "Predicción creada exitosamente",
        "prediccionid": prediccion.prediccionid,
        "modeloid": prediccion.modeloid,
        "periodoid": prediccion.periodoid,
        "prediccion": str(prediccion.prediccion)
    }), 201
@predicciones_bp.route('/api/predicciones/generar', methods=['POST'])
def generar_predicciones():

    data = request.get_json(silent=True) or {}

    requeridos = ("templateid", "sucursalid", "inicio")
    if not all(k in data for k in requeridos):
        return jsonify({
            "error": "templateid, sucursalid e inicio son requeridos"
        }), 400

    templateid  = int(data["templateid"])
    sucursalid  = int(data["sucursalid"])
    inicio_anio = int(data["inicio"]["anio"])
    inicio_mes  = int(data["inicio"]["mes"])

    n_periodos = data.get("n_periodos")
    fin = data.get("fin")

    if not n_periodos and not fin:
        return jsonify({
            "error": "Debe enviar fin o n_periodos"
        }), 400

    # 1️⃣ Obtener modelos del template y sucursal
    modelos = (
        Modelo.query
        .join(CuentaContable, CuentaContable.cuentaid == Modelo.cuentaid)
        .filter(
            CuentaContable.templateid == templateid,
            Modelo.sucursalid == sucursalid
        )
        .all()
    )

    if not modelos:
        return jsonify({"error": "No hay modelos para este template"}), 404

    # 2️⃣ Calcular periodos destino
    periodos_destino = []

    if n_periodos:
        anio, mes = inicio_anio, inicio_mes
        for _ in range(int(n_periodos)):
            periodo = Periodo.query.filter_by(anio=anio, mes=mes).first()
            if periodo:
                periodos_destino.append(periodo)
            mes += 1
            if mes > 12:
                mes = 1
                anio += 1

    else:
        fin_anio = int(fin["anio"])
        fin_mes  = int(fin["mes"])

        periodos_destino = (
            Periodo.query
            .filter(
                (Periodo.anio > inicio_anio) |
                ((Periodo.anio == inicio_anio) & (Periodo.mes >= inicio_mes)),
                (Periodo.anio < fin_anio) |
                ((Periodo.anio == fin_anio) & (Periodo.mes <= fin_mes))
            )
            .order_by(Periodo.anio, Periodo.mes)
            .all()
        )

    if not periodos_destino:
        return jsonify({"error": "No existen periodos destino"}), 400

    # 3️⃣ Ejecutar predicciones
    from joblib import load

    resumen = []

    for modelo in modelos:
        model_path = modelo.ubicacion
        try:
            predictor = load(model_path)
        except Exception as e:
            return jsonify({
                "error": "No se pudo cargar el modelo",
                "modelo": model_path,
                "detalle": str(e)
            }), 500

        for periodo in periodos_destino:
            valor_predicho = float(predictor.predict(1)[0])  # ajustable

            pred = Prediccion(
                modeloid=modelo.modeloid,
                periodoid=periodo.periodoid,
                prediccion=valor_predicho
            )
            db.session.add(pred)

            resumen.append({
                "modeloid": modelo.modeloid,
                "cuentaid": modelo.cuentaid,
                "periodoid": periodo.periodoid,
                "anio": periodo.anio,
                "mes": periodo.mes,
                "prediccion": valor_predicho
            })

    db.session.commit()

    return jsonify({
        "message": "Predicciones generadas correctamente",
        "templateid": templateid,
        "sucursalid": sucursalid,
        "total_predicciones": len(resumen),
        "predicciones": resumen
    }), 201
@predicciones_bp.route('/api/predicciones/listar', methods=['POST'])
def listar_predicciones():

    data = request.get_json(silent=True) or {}

    templateid = data.get("templateid")
    sucursalid = data.get("sucursalid")

    if not templateid or not sucursalid:
        return jsonify({
            "error": "templateid y sucursalid son requeridos"
        }), 400

    resultados = (
        db.session.query(
            Prediccion.prediccionid,
            Modelo.modeloid,
            Modelo.modelo,
            CuentaContable.cuentaid,
            CuentaContable.codigo,
            CuentaContable.nombre,
            Periodo.periodoid,
            Periodo.anio,
            Periodo.mes,
            Prediccion.prediccion
        )
        .join(Modelo, Modelo.modeloid == Prediccion.modeloid)
        .join(CuentaContable, CuentaContable.cuentaid == Modelo.cuentaid)
        .join(Periodo, Periodo.periodoid == Prediccion.periodoid)
        .filter(
            CuentaContable.templateid == templateid,
            Modelo.sucursalid == sucursalid
        )
        .order_by(Periodo.anio, Periodo.mes, CuentaContable.codigo)
        .all()
    )

    predicciones = []
    for r in resultados:
        predicciones.append({
            "prediccionid": r.prediccionid,
            "modeloid": r.modeloid,
            "modelo": r.modelo,
            "cuentaid": r.cuentaid,
            "codigo": r.codigo,
            "cuenta": r.nombre,
            "periodoid": r.periodoid,
            "anio": r.anio,
            "mes": r.mes,
            "prediccion": float(r.prediccion)
        })

    return jsonify({
        "templateid": templateid,
        "sucursalid": sucursalid,
        "total": len(predicciones),
        "predicciones": predicciones
    }), 200
@predicciones_bp.route('/api/predicciones/comparar', methods=['POST'])
def comparar_saldos_vs_predicciones():

    data = request.get_json(silent=True) or {}

    templateid = data.get("templateid")
    sucursalid = data.get("sucursalid")

    if not templateid or not sucursalid:
        return jsonify({
            "error": "templateid y sucursalid son requeridos"
        }), 400

    resultados = (
        db.session.query(
            CuentaContable.codigo,
            CuentaContable.nombre.label("cuenta"),
            Periodo.anio,
            Periodo.mes,
            SaldoMensualCTS.saldo.label("saldo_real"),
            Prediccion.prediccion.label("saldo_predicho")
        )
        .join(SaldoMensualCTS, SaldoMensualCTS.cuentaid == CuentaContable.cuentaid)
        .join(Periodo, Periodo.periodoid == SaldoMensualCTS.periodoid)
        .join(Modelo, Modelo.cuentaid == CuentaContable.cuentaid)
        .join(Prediccion,
              (Prediccion.modeloid == Modelo.modeloid) &
              (Prediccion.periodoid == Periodo.periodoid)
        )
        .filter(
            CuentaContable.templateid == templateid,
            SaldoMensualCTS.sucursalid == sucursalid,
            Modelo.sucursalid == sucursalid
        )
        .order_by(Periodo.anio, Periodo.mes, CuentaContable.codigo)
        .all()
    )

    comparativo = []
    for r in resultados:
        saldo_real = float(r.saldo_real)
        saldo_pred = float(r.saldo_predicho)
        diferencia = saldo_pred - saldo_real
        error_pct = None

        if saldo_real != 0:
            error_pct = round((diferencia / saldo_real) * 100, 2)

        comparativo.append({
            "codigo": r.codigo,
            "cuenta": r.cuenta,
            "anio": r.anio,
            "mes": r.mes,
            "saldo_real": saldo_real,
            "saldo_predicho": saldo_pred,
            "diferencia": round(diferencia, 2),
            "error_pct": error_pct
        })

    return jsonify({
        "templateid": templateid,
        "sucursalid": sucursalid,
        "total": len(comparativo),
        "comparativo": comparativo
    }), 200
@predicciones_bp.route('/api/predicciones/sucursal', methods=['POST'])
def predicciones_por_sucursal():
    """
    Body JSON:
    {
        "sucursalid": 1
    }
    """
    data = request.get_json()
    sucursalid = data.get("sucursalid")
    if not sucursalid:
        return jsonify({"error": "sucursalid es requerido"}), 400

    # Obtener templates activos de la sucursal
    templates_activos = db.session.query(SucursalTemplate.templateid).filter_by(sucursalid=sucursalid, activo=True).subquery()

    # Cuentas contables de esos templates
    cuentas = db.session.query(CuentaContable.cuentaid).filter(CuentaContable.templateid.in_(templates_activos)).subquery()

    # Obtener los Modelos asociados a esas cuentas contables
    modelos = db.session.query(Modelo.modeloid).filter(Modelo.cuentaid.in_(cuentas)).subquery()

    # Obtener predicciones de esos modelos
    predicciones = Prediccion.query.filter(Prediccion.modeloid.in_(modelos)).all()

    resultado = [
        {
            "prediccionid": p.prediccionid,
            "modeloid": p.modeloid,
            "periodoid": p.periodoid,
            "valor": float(p.prediccion)
        } for p in predicciones
    ]

    return jsonify(resultado)