from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Template_Balance, Institution, InstitutionTemplate

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
    templates = Template_Balance.query.all()

    return jsonify([
        {
            "templateid": t.templateid,
            "nombre": t.nombre,
            "descripcion": t.descripcion,
            "created_at": t.created_at
        }
        for t in templates
    ])
