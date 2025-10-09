from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Escenario, EscenarioCuenta, CuentaContable, Modelo, Periodo, Prediccion

import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime


escenario_bp = Blueprint('escenario_bp', __name__)
# Crear un escenario
@escenario_bp.route('/api/escenario/create', methods=['POST'])
def create_escenario():
    data = request.get_json()

    try:
        escenario = Escenario(
            nombre=data['nombre'],
            tipo=data['tipo'],
            description=data.get('description'),
            inicio=data['inicio'],   # JSON (ej: {"anio":2025,"mes":9})
            fin=data['fin']          # JSON
        )
        db.session.add(escenario)
        db.session.commit()

        return jsonify({"message": "Escenario creado", "escenarioid": escenario.escenarioid}), 201
    except KeyError as e:
        return jsonify({"error": f"Falta el campo: {str(e)}"}), 400


# Listar todos los escenarios
@escenario_bp.route('/api/escenario/list', methods=['POST'])
def list_escenarios():
    escenarios = Escenario.query.all()
    return jsonify([
        {
            "escenarioid": e.escenarioid,
            "nombre": e.nombre,
            "tipo": e.tipo,
            "description": e.description,
            "elaboracion": e.elaboracion.isoformat(),
            "inicio": e.inicio,
            "fin": e.fin
        } for e in escenarios
    ])

# Cargar el modelo .pkl una sola vez
MODEL_PATH = os.path.join("modelos", "/root/proyecciones/ProyeccionFinanciera/instituciones/institucion_1/sucursal_0/101/RidgePSO_3_101.pkl")
best_model = joblib.load(MODEL_PATH)
@escenario_bp.route("/api/escenario/prediccion", methods=["POST"])
def api_validate_escenario():
    """
    Body JSON esperado mínimo:
    { "escenarioid": 5 }

    Opcionalmente puedes enviar:
    {
        "escenarioid": 5,
        "cuentas": ["1001","1100"]       # lista de códigos (strings)
        # o "cuentas": [101, 102]        # lista de cuentaid (ints)
    }
    """
    data = request.get_json()
    if not data or "escenarioid" not in data:
        return jsonify({"status": "error", "message": "Se requiere 'escenarioid' en el body."}), 400

    escenarioid = data["escenarioid"]

    # 1) validar que exista el escenario
    escenario = Escenario.query.get(escenarioid)
    if not escenario:
        return jsonify({
            "status": "error",
            "message": f"El escenario con id {escenarioid} no existe."
        }), 404

    anio_ini = escenario.inicio["anio"]
    mes_ini = escenario.inicio["mes"]
    anio_fin = escenario.fin["anio"]
    mes_fin = escenario.fin["mes"]

    # Generar la fecha de inicio y fin en formato AAAA-MM-01
    fecha_inicio = f"{anio_ini}-{mes_ini:02d}-01"
    fecha_fin    = f"{anio_fin}-{mes_fin:02d}-01"

    # Rango mensual
    fechas_pred = pd.date_range(start=fecha_inicio, end=fecha_fin, freq="MS")  # MS = Month Start
    fechas_formateadas = fechas_pred.strftime("%Y-%m-%d").tolist()

    # Número de meses
    num_meses = len(fechas_formateadas)


    # 2) obtener relaciones en escenariocuenta para ese escenario
    relaciones = EscenarioCuenta.query.filter_by(escenarioid=escenarioid).all()
    if not relaciones:
        return jsonify({
            "status": "error",
            "message": f"No hay cuentas asociadas al escenario {escenarioid}."
        }), 400
    
    cuenta_ids = [r.cuentaid for r in relaciones]

    # 3) Obtener modelos asociados a esas cuentas
    # JOIN para traer CuentaContable y Modelo
    modelos = (
        db.session.query(Modelo)
        .join(CuentaContable, CuentaContable.cuentaid == Modelo.cuentaid)
        .filter(Modelo.cuentaid.in_(cuenta_ids))
        .all()
    )

    if not modelos:
        return jsonify({
            "status": "error",
            "message": "No se encontraron modelos entrenados para las cuentas de este escenario."
        }), 400
    print(modelos)
    """
    # Estructurar respuesta: cuenta + modelo
    modelos_info = []
    for m in modelos:
        modelos_info.append({
            "modeloid": m.modeloid,
            "cuentaid": m.cuentaid,
            "codigo": m.cuenta.codigo,
            "nombre_cuenta": m.cuenta.nombre,
            "modelo": m.modelo,
            "ubicacion": m.ubicacion,
            "variables": m.variables
        }) 
    """

    # 4️⃣ Predecir con cada modelo
    resultados_pred = []
    for m in modelos:
        try:
            # Cargar modelo entrenado desde su ubicación
            model_path = m.ubicacion
            if not os.path.exists(model_path):
                resultados_pred.append({
                    "modeloid": m.modeloid,
                    "cuentaid": m.cuentaid,
                    "codigo": m.cuenta.codigo,
                    "error": f"No se encontró el archivo del modelo en {model_path}"
                })
                continue

            modelo_entrenado = joblib.load(model_path)
            if m.cuenta.codigo == '101':
                historial_inicial = [24594283,14745669,20649258]
            if m.cuenta.codigo == '102':
                historial_inicial = [264317279,273679263,270785509]
            # Crear los pasos de predicción. Ej: si el modelo fue entrenado con X=[[0],[1],...]
            predicciones = []
            for _ in range(num_meses):
                entrada = np.array(historial_inicial[-num_meses:]).reshape(1, -1)
    
                prediccion = modelo_entrenado.predict(entrada)[0]
                predicciones.append(prediccion)

            resultados_pred.append({
                "modeloid": m.modeloid,
                "cuentaid": m.cuentaid,
                "codigo": m.cuenta.codigo,
                "nombre_cuenta": m.cuenta.nombre,
                "fechas_pred": fechas_formateadas,
                "predicciones": [round(float(p),2) for p in predicciones]
            })
            """
                Se tiene que hacer un insert a la tabla predicciones

                prediccion = Prediccion(modeloid=modeloid, periodoid=periodoid, prediccion=valor)
                db.session.add(prediccion)
                db.session.commit()


                fechas_formateadas --> debemos quitar el anio y periodo y consultarlo en la tabla periodo
            """
            for i,fe in enumerate(fechas_formateadas):
                dt = datetime.strptime(fe, "%Y-%m-%d")
                anio = dt.year
                mes = dt.month

                periodo = Periodo.query.filter_by(anio=anio, mes=mes).first()
                if not periodo:
                    return jsonify({
                        "status": "error",
                        "message": "No se encontro el periodo en la tabla Periodo."
                    }), 400
                print(periodo.periodoid, "    ", predicciones[i])
                prediction = round(float(predicciones[i]),2)
                prediccion = Prediccion(modeloid=m.modeloid, periodoid=periodo.periodoid, prediccion=prediction)
                db.session.add(prediccion)
                db.session.commit()

        except Exception as e:
            resultados_pred.append({
                "modeloid": m.modeloid,
                "cuentaid": m.cuentaid,
                "codigo": m.cuenta.codigo,
                "error": f"Error al predecir: {str(e)}"
            })
        
    # 4) OK: devolver info del escenario y las cuentas asociadas
    return jsonify({
        "status": "ok",
        "escenario": {
            "escenarioid": escenario.escenarioid,
            "inicio": escenario.inicio,
            "fin":escenario.fin,
            "nombre": getattr(escenario, "nombre", None), 
            "fechas": fechas_formateadas,
            "totalmeses": num_meses
        },
        #"modelos": modelos_info
        "predicciones": resultados_pred
    }), 200
