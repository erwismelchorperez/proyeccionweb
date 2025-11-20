from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Template_Balance, Institution, InstitutionTemplate, TempInd, CuentaContable, SaldoMensualCTS, Semaforo

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
    relacionados_tempind = TempInd.query.filter_by(templateid=template_id).count()
    if relacionados_tempind > 0:
        return jsonify({
            "error": "No se puede eliminar el template porque está asociado a indicadores.",
            "detalle": f"Indicadores relacionados: {relacionados_tempind}"
        }), 400

    # 3. Validar cuentas contables relacionadas
    cuentas = CuentaContable.query.filter_by(templateid=template_id).all()

    if cuentas:
        # Revisar si esas cuentas tienen saldos
        cuenta_ids = [c.cuentaid for c in cuentas]

        periodos_saldos = db.session.query(
            SaldoMensualCTS.periodo
        ).filter(
            SaldoMensualCTS.cuentaid.in_(cuenta_ids)
        ).distinct().count()

        if periodos_saldos > 0:
            return jsonify({
                "error": "No se puede eliminar el template porque las cuentas tienen saldos registrados.",
                "periodos_registrados": periodos_saldos
            }), 400

    # 4. Validar semáforos asociados
    semaforos = Semaforo.query.filter_by(templateid=template_id).count()
    if semaforos > 0:
        return jsonify({
            "error": "No se puede eliminar el template porque tiene semáforos configurados.",
            "semaforos_relacionados": semaforos
        }), 400

    # 5. Si pasa todas las validaciones → eliminar template
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
