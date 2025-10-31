from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Template_Balance, Institution, InstitutionTemplate, TempInd, CuentaContable, SaldoMensualCTS

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
    data = request.json
    flagdelete = False

    if not data or 'templateid' not in data:
        return jsonify({"error": "Se requiere el campo 'templateid'"}), 400

    template = Template_Balance.query.get(data['templateid'])
    if not template:
        return jsonify({"error": f"No se encontró el template con ID {data['templateid']}"}), 404
    
    # Obtener las cuentas asociadas a este template
    cuentas = CuentaContable.query.filter_by(templateid=template.templateid).all()
    if not cuentas:
        return jsonify({"error": "No hay cuentas asociadas a este template"}), 400

    # Obtener IDs de las cuentas
    cuenta_ids = [c.cuentaid for c in cuentas]

    # Contar periodos distintos en saldo_balance_cts para estas cuentas
    periodos_count = db.session.query(
        SaldoMensualCTS.periodoid
    ).filter(SaldoMensualCTS.cuentaid.in_(cuenta_ids)).distinct().count()

    if periodos_count > 2:
        return jsonify({
            "error": f"No se puede eliminar el template porque tiene {periodos_count} periodos capturados en saldo_balance_cts"
        }), 400
    print(periodos_count)
    """
    # Contar periodos en la tabla saldos asociados a este template
    periodos = db.session.query(Saldo.templateid, Saldo.periodo).filter(Saldo.templateid == template.templateid).distinct().count()
    
    if periodos > 2:
        return jsonify({"error": "No se puede eliminar el template porque tiene más de 2 periodos capturados"}), 400
    
    try:
        db.session.delete(template)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Ocurrió un error al eliminar el template", "details": str(e)}), 500
    """
    print(template)
    return jsonify({"message": f"Template con ID {template.templateid} eliminado correctamente"}), 200
