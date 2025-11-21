from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Template_Balance, Institution, InstitutionTemplate, TempInd, CuentaContable, SaldoMensualCTS, Semaforo, ValorIndicador, ValorVariable, TempVar, Periodo

template_balance_bp = Blueprint('template_balance_bp', __name__)

# 📌 Crear un template balance
@template_balance_bp.route('/api/Createtemplate', methods=['POST'])
def api_crear_template():
    data = request.get_json()

    if not data or "nombre" not in data or "institutionid" not in data:
        return jsonify({"error": "Los campos 'nombre' e 'institutionid' son requeridos"}), 400

    institution_id = data["institutionid"]

    # Validar existencia de la institution
    institution = Institution.query.get(institution_id)
    if not institution:
        return jsonify({"error": "La institution especificada no existe"}), 404

    # 1️⃣ Crear el template
    template = Template_Balance(
        nombre=data["nombre"],
        descripcion=data.get("descripcion")
    )
    db.session.add(template)
    db.session.flush()  # Necesario para obtener template.templateid sin hacer commit todavía

    # 2️⃣ Buscar si ya hay un template activo para esta institution
    template_existente = InstitutionTemplate.query.filter_by(
        institutionid=institution_id,
        activo=True
    ).first()

    if template_existente:
        template_existente.activo = False
        db.session.add(template_existente)

    # 3️⃣ Crear la nueva relación como activa
    nueva_relacion = InstitutionTemplate(
        institutionid=institution_id,
        templateid=template.templateid,
        activo=True
    )
    db.session.add(nueva_relacion)
    db.session.commit()

    return jsonify({
        "message": "Template creado y relación con institution registrada correctamente",
        "template": {
            "templateid": template.templateid,
            "nombre": template.nombre,
            "descripcion": template.descripcion,
            "created_at": template.created_at
        },
        "institution_template": {
            "insttempid": nueva_relacion.insttempid,
            "institutionid": nueva_relacion.institutionid,
            "templateid": nueva_relacion.templateid,
            "activo": nueva_relacion.activo
        }
    }), 201

# 📌 Actualizar un template balance
@template_balance_bp.route('/api/Updatetemplate', methods=['POST'])
def api_update_template():
    data = request.get_json()

    if not data or "templateid" not in data:
        return jsonify({"error": "templateid es requerido"}), 400

    template = Template_Balance.query.get(data["templateid"])
    if not template:
        return jsonify({"error": "Template no encontrado"}), 404

    # Actualizar valores
    template.nombre = data.get("nombre", template.nombre)
    template.descripcion = data.get("descripcion", template.descripcion)
    #template.clavepais = data.get("clavepais", template.clavepais)

    db.session.commit()

    return jsonify({
        "message": "Template actualizado exitosamente",
        "template": {
            "templateid": template.templateid,
            "nombre": template.nombre,
            "descripcion":template.descripcion,
            "created_at": template.created_at
        }
    })


# 📌 Listar todos los templates de una sucursal
@template_balance_bp.route('/api/Listtemplates', methods=['GET','POST'])
def api_list_templates():
    try:
        templates = Template_Balance.query.all()
        result = []

        for t in templates:
            # Obtener las relaciones institution_template para este template
            rels = InstitutionTemplate.query.filter_by(templateid=t.templateid).all()
            institucion_ids = [r.institutionid for r in rels]

            instituciones = []
            if institucion_ids:
                instituciones_query = (
                    db.session.query(Institution)
                    .filter(Institution.institutionid.in_(institucion_ids))
                    .all()
                )

                instituciones = [
                    {
                        "institutionid": inst.institutionid,
                        "nombre": getattr(inst, "nombre", None),
                        "alias": getattr(inst, "alias", None),
                        "clavepais": getattr(inst, "country", None),
                        "activo_relacion": next((r.activo for r in rels if r.institutionid == inst.institutionid), None)
                    }
                    for inst in instituciones_query
                ]

            result.append({
                "templateid": t.templateid,
                "nombre": t.nombre,
                "descripcion": t.descripcion,
                "created_at": t.created_at,
                "instituciones": instituciones
            })

        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Error al obtener los templates con sus instituciones",
            "detalle": str(e)
        }), 500
@template_balance_bp.route('/api/template/delete', methods=['DELETE'])
def delete_template():
    data = request.get_json() or {}

    # Validación del campo requerido
    if "templateid" not in data:
        return jsonify({"error": "Se requiere el campo 'templateid'"}), 400

    template_id = data["templateid"]

    # 1. Verificar que el template exista
    template = Template_Balance.query.get(template_id)
    if not template:
        return jsonify({"error": "El template no existe"}), 404

    # 2. Validar relación con TempInd (indicadores asignados)
    tempind_rel = TempInd.query.filter_by(templateid=template_id).all()
    if tempind_rel:
        # Obtener lista de ids de indicadores asociados al template
        indicador_ids = [ti.indicadorid for ti in tempind_rel]

        # Validar registros en valorIndicador
        registros_valor_ind = db.session.query(ValorIndicador) \
            .filter(ValorIndicador.indicadorid.in_(indicador_ids)) \
            .count()

        if registros_valor_ind > 0:
            return jsonify({
                "error": "No se puede eliminar el template porque sus indicadores tienen datos registrados.",
                "detalle": f"Registros en valorIndicador: {registros_valor_ind}"
            }), 400
        """
        # Si NO tiene registros en valorIndicador pero sí tiene indicadores, avisar igual
        return jsonify({
            "error": "No se puede eliminar el template porque está asociado a indicadores.",
            "detalle": f"Indicadores relacionados: {len(indicador_ids)}"
        }), 400
        """

    
    # 3. Validar cuentas contables relacionadas
    cuentas = CuentaContable.query.filter_by(templateid=template_id).all()

    if cuentas:
        cuenta_ids = [c.cuentaid for c in cuentas]

        # Buscar periodos usados en saldos
        periodos_en_saldos = db.session.query(
            SaldoMensualCTS.periodoid
        ).filter(
            SaldoMensualCTS.cuentaid.in_(cuenta_ids)
        ).distinct().all()

        if periodos_en_saldos:
            # Extraer IDs como lista simple
            periodo_ids = [p[0] for p in periodos_en_saldos]

            # Ahora consultar detalles en la tabla Periodo
            periodos_detalle = Periodo.query.filter(
                Periodo.periodoid.in_(periodo_ids)
            ).all()

            # Preparar detalle amigable
            lista_periodos = [
                {
                    "periodoid": p.periodoid,
                    "anio": p.anio,
                    "mes": p.mes
                } for p in periodos_detalle
            ]

            return jsonify({
                "error": "No se puede eliminar el template porque las cuentas tienen saldos registrados.",
                "periodos_registrados": lista_periodos,
                "total_periodos": len(lista_periodos)
            }), 400
    """
    # 4. Validar semáforos asociados
    semaforos = Semaforo.query.filter_by(templateid=template_id).count()
    if semaforos > 0:
        return jsonify({
            "error": "No se puede eliminar el template porque tiene semáforos configurados.",
            "semaforos_relacionados": semaforos
        }), 400
    """    
    # 5. Validar variables relacionadas al template
    variables_rel = TempVar.query.filter_by(templateid=template_id).all()
    if variables_rel:
        # Obtener ids de variables asociadas
        variable_ids = [v.variableid for v in variables_rel]

        # Validar si esas variables tienen registros en valorVariable
        registros_valor_variable = db.session.query(ValorVariable) \
            .filter(ValorVariable.variableid.in_(variable_ids)) \
            .count()

        if registros_valor_variable > 0:
            return jsonify({
                "error": "No se puede eliminar el template porque sus variables tienen datos registrados.",
                "detalle": f"Registros en valorVariable: {registros_valor_variable}"
            }), 400

        """
        # Si tienen variables pero no valorVariable → aun así prohibimos la eliminación
        return jsonify({
            "error": "No se puede eliminar el template porque tiene variables asociadas.",
            "detalle": f"Variables relacionadas: {len(variable_ids)}"
        }), 400
        """

    # 6. Si pasa todas las validaciones → eliminar template
    try:
        db.session.delete(template)
        db.session.commit()

        return jsonify({
            "message": f"Template {template_id} eliminado correctamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Error interno al intentar eliminar el template",
            "detalle": str(e)
        }), 500
