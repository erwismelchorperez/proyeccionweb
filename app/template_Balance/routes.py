from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Template_Balance

template_balance_bp = Blueprint('template_balance_bp', __name__)

# 📌 Crear un template balance
@template_balance_bp.route('/api/Createtemplate', methods=['POST'])
def api_crear_template():
    data = request.get_json()

    if not data or "nombre" not in data:
        return jsonify({"error": "nombre datos son requeridos"}), 400

    template = Template_Balance(
        nombre=data["nombre"],
        descripcion=data.get("descripcion")
    )

    db.session.add(template)
    db.session.commit()

    return jsonify({
        "message": "Template creado exitosamente",
        "template": {
            "templateid": template.templateid,
            "nombre": template.nombre,
            "descripcion": template.descripcion,
            "created_at": template.created_at
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
@template_balance_bp.route('/api/Listtemplates', methods=['POST'])
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
