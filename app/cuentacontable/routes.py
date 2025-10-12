from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import CuentaContable, TipoCuenta, ValidacionesCtgoCts, Template_Balance, SaldoMensualCTS, Periodo

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
@cuentacontable_bp.route('/api/GenerarValTemplate', methods=['POST'])
def api_validar_template():
    data = request.get_json()
    templateid = data.get("templateid")

    if not templateid:
        return jsonify({"error": "es necesario templateid son requeridos"}), 400

    # 🔹 Llamada a la función PostgreSQL
    sql = text("SELECT public.generarvalidaciones(:templateid)")
    result = db.session.execute(sql, {"templateid": templateid}).scalar()

    return jsonify({
        "message": "Validaciones creadas correctamente",
        "resultado": result
    }), 200
@cuentacontable_bp.route('/api/validaciones/create', methods=['POST'])
def crear_validacion():
    data = request.get_json()

    templateid     = data.get("templateid")
    tipo_input     = data.get("tipo")
    nivel          = data.get("nivel")
    description    = data.get("description")
    cuentaobjetivo = data.get("cuentaobjetivo")
    expresion      = data.get("expresion")
    operador       = data.get("operador")
    validacion     = data.get("validacion", True)

    # -----------------------------
    # 1️⃣ Validar template requerido
    # -----------------------------
    if not templateid:
        return jsonify({"error": "El campo 'templateid' es requerido"}), 400

    template = Template_Balance.query.get(templateid)
    if not template:
        return jsonify({"error": "No existe el template especificado"}), 404

    # -----------------------------
    # 2️⃣ Validar y resolver tipo
    # -----------------------------
    if not tipo_input:
        return jsonify({"error": "El campo 'tipo' es requerido"}), 400

    tipo_id = None

    if isinstance(tipo_input, int):
        # Buscar por ID
        tipo_obj = TipoCuenta.query.get(tipo_input)
        if not tipo_obj:
            return jsonify({"error": f"No existe un tipo de cuenta con id {tipo_input}"}), 400
        tipo_id = tipo_obj.tipocuentaid
    else:
        # Buscar por nombre o clave tipo (si tu modelo tiene 'clavetipo' además de 'nombre')
        tipo_obj = TipoCuenta.query.filter(
            (TipoCuenta.nombre == tipo_input) | (TipoCuenta.clavetipo == tipo_input)
        ).first()

        if not tipo_obj:
            return jsonify({"error": f"No existe un tipo de cuenta con nombre o clave '{tipo_input}'"}), 400

        tipo_id = tipo_obj.tipocuentaid

    # -----------------------------
    # 3️⃣ Crear la nueva validación
    # -----------------------------
    nueva_validacion = ValidacionesCtgoCts(
        templateid=templateid,
        tipo=tipo_id,
        nivel=nivel,
        description=description,
        cuentaobjetivo=cuentaobjetivo,
        expresion=expresion,
        operador=operador,
        validacion=bool(validacion)
    )

    db.session.add(nueva_validacion)
    db.session.commit()

    return jsonify({
        "message": "Validación creada exitosamente",
        "validacionesid": nueva_validacion.validacionesid,
        "tipoid": tipo_id
    }), 201
# Actualizar validación
@cuentacontable_bp.route('/api/validaciones/update', methods=['POST'])
def update_validacion():
    data = request.get_json()
    validacionesid = data.get('validacionesid')

    validacion = ValidacionesCtgoCts.query.get(validacionesid)
    if not validacion:
        return jsonify({"error": "Validación no encontrada"}), 404

    # --- Validar o resolver el tipo ---
    tipo_id = None
    if 'tipo' in data:
        tipo_valor = data['tipo']

        # Si viene un número, se asume que es el ID directamente
        if isinstance(tipo_valor, int):
            tipo_existente = TipoCuenta.query.get(tipo_valor)
            if not tipo_existente:
                return jsonify({"error": f"El tipo con id {tipo_valor} no existe"}), 400
            tipo_id = tipo_valor
        else:
            # Si viene el nombre, buscarlo
            tipo_existente = TipoCuenta.query.filter_by(clavetipo=tipo_valor).first()
            if not tipo_existente:
                return jsonify({"error": f"No existe un tipo de cuenta con el nombre '{tipo_valor}'"}), 400
            tipo_id = tipo_existente.tipocuentaid

    # --- Actualizar campos ---
    for field in ['templateid', 'description', 'cuentaobjetivo', 'expresion', 'operador', 'validacion', 'nivel']:
        if field in data:
            setattr(validacion, field, data[field])

    # Si se determinó un tipo válido, asignarlo
    if tipo_id is not None:
        validacion.tipo = tipo_id

    db.session.commit()

    return jsonify({
        "message": "Validación actualizada correctamente",
        "validacion": validacion.to_dict()
    }), 200
# Eliminar validación
@cuentacontable_bp.route('/api/validaciones/delete', methods=['POST'])
def delete_validacion():
    data = request.get_json()
    validacionesid = data.get('validacionesid')

    validacion = ValidacionesCtgoCts.query.get(validacionesid)
    if not validacion:
        return jsonify({"error": "Validación no encontrada"}), 404

    db.session.delete(validacion)
    db.session.commit()

    return jsonify({"message": "Validación eliminada correctamente"}), 200
@cuentacontable_bp.route('/api/validaciones/list', methods=['POST'])
def listar_validaciones():
    data = request.get_json()
    templateid = data.get("templateid")

    if not templateid:
        return jsonify({"error": "templateid es requerido"}), 400

    validaciones = ValidacionesCtgoCts.query.filter_by(templateid=templateid).all()

    resultado = [
        {
            "validacionesid": v.validacionesid,
            "templateid": v.templateid,
            "tipo": v.tipo,
            "nivel": v.nivel,
            "description": v.description,
            "cuentaobjetivo": v.cuentaobjetivo,
            "expresion": v.expresion,
            "operador": v.operador,
            "validacion": v.validacion
        }
        for v in validaciones
    ]

    return jsonify({
        "message": "Validaciones encontradas",
        "templateid": templateid,
        "validaciones": resultado
    }), 200
@cuentacontable_bp.route('/api/validaciones/verificar_template', methods=['POST'])
def verificar_validaciones_template():
    data = request.get_json()
    templateid = data.get("templateid")

    if not templateid:
        return jsonify({"error": "El campo 'templateid' es requerido"}), 400

    # ------------------------------
    # 1️⃣ Buscar todas las validaciones del template
    # ------------------------------
    validaciones = ValidacionesCtgoCts.query.filter_by(templateid=templateid).all()
    if not validaciones:
        return jsonify({"error": "No hay validaciones registradas para este template"}), 404

    # ------------------------------
    # 2️⃣ Buscar las cuentas del template
    # ------------------------------
    cuentas = {str(c.codigo): c.cuentaid for c in CuentaContable.query.filter_by(templateid=templateid).all()}

    if not cuentas:
        return jsonify({"error": "No existen cuentas asociadas al template"}), 400

    # ------------------------------
    # 3️⃣ Determinar el último periodo con saldos
    # ------------------------------
    ultimo_periodo = (
        db.session.query(Periodo)
        .join(SaldoMensualCTS, SaldoMensualCTS.periodoid == Periodo.periodoid)
        .join(CuentaContable, CuentaContable.cuentaid == SaldoMensualCTS.cuentaid)
        .filter(CuentaContable.templateid == templateid)
        .order_by(Periodo.anio.desc(), Periodo.mes.desc())
        .first()
    )

    if not ultimo_periodo:
        return jsonify({"error": "No hay saldos registrados para este template"}), 404

    # ------------------------------
    # 4️⃣ Cargar todos los saldos del periodo
    # ------------------------------
    saldos = {
        str(s.cuentaid): float(s.saldo)
        for s in SaldoMensualCTS.query.filter_by(periodoid=ultimo_periodo.periodoid).all()
    }

    resultados = []
    import re

    # ------------------------------
    # 5️⃣ Procesar cada validación
    # ------------------------------
    for v in validaciones:
        expresion = v.expresion
        operador = v.operador
        cuenta_obj = v.cuentaobjetivo  # puede ser None

        # Validar campos mínimos
        if not expresion or not operador:
            resultados.append({
                "validacionesid": v.validacionesid,
                "description": v.description,
                "error": "Campos incompletos en la validación"
            })
            continue

        # Resolver expresión: ejemplo "+ 501 + 502 - 503"
        tokens = re.findall(r'[+-]?\s*\d+', expresion)
        total_exp = 0.0
        error_flag = False

        for token in tokens:
            token = token.replace(" ", "")
            signo = 1
            if token.startswith('+'):
                token = token[1:]
            elif token.startswith('-'):
                signo = -1
                token = token[1:]

            cuentaid = cuentas.get(token)
            saldo = saldos.get(str(cuentaid), 0.0) if cuentaid else 0.0
            total_exp += signo * saldo

        # ------------------------------
        # Evaluar resultado según la regla nueva
        # ------------------------------
        if cuenta_obj is None:
            # Cuenta objetivo NULL → expresión debe dar 0
            cumple = abs(total_exp) < 1e-6
            saldo_obj = None
            comparacion = f"{total_exp} == 0"
        else:
            # Cuenta objetivo existe o no
            cuentaid_obj = cuentas.get(str(cuenta_obj))
            saldo_obj = saldos.get(str(cuentaid_obj), 0.0) if cuentaid_obj else None

            if saldo_obj is None:
                # Cuenta objetivo no existe → solo mostrar resultado de la expresión
                cumple = True  # Se considera válida solo por no tener cuenta objetivo real
                comparacion = f"Cuenta objetivo {cuenta_obj} no existe, resultado_expr={total_exp}"
            else:
                # Comparar según operador
                if operador == "=":
                    cumple = abs(saldo_obj - total_exp) < 1e-6
                    comparacion = f"{saldo_obj} == {total_exp}"
                elif operador == ">":
                    cumple = saldo_obj > total_exp
                    comparacion = f"{saldo_obj} > {total_exp}"
                elif operador == "<":
                    cumple = saldo_obj < total_exp
                    comparacion = f"{saldo_obj} < {total_exp}"
                elif operador == ">=":
                    cumple = saldo_obj >= total_exp
                    comparacion = f"{saldo_obj} >= {total_exp}"
                elif operador == "<=":
                    cumple = saldo_obj <= total_exp
                    comparacion = f"{saldo_obj} <= {total_exp}"
                else:
                    resultados.append({
                        "validacionesid": v.validacionesid,
                        "description": v.description,
                        "error": f"Operador '{operador}' no válido"
                    })
                    continue

        resultados.append({
            "validacionesid": v.validacionesid,
            "description": v.description,
            "cuenta_objetivo": cuenta_obj,
            "saldo_objetivo": saldo_obj,
            "valor_expresion": total_exp,
            "operador": operador,
            "cumple": cumple
        })

    # ------------------------------
    # 6️⃣ Resumen general
    # ------------------------------
    total = len(resultados)
    exitosas = sum(1 for r in resultados if r.get("cumple") is True)
    fallidas = total - exitosas

    return jsonify({
        "message": "Validaciones evaluadas correctamente",
        "templateid": templateid,
        "periodo": f"{ultimo_periodo.mes}/{ultimo_periodo.anio}",
        "total_validaciones": total,
        "cumplen": exitosas,
        "no_cumplen": fallidas,
        "resultados": resultados
    }), 200