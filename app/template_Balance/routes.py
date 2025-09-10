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

    if not data or "sucursalid" not in data or "nombre" not in data:
        return jsonify({"error": "sucursalid y nombre son requeridos"}), 400

    # Si este template se marca como activo, desactivar los demás de la misma sucursal
    if data.get("activo", False):
        Template_Balance.query.filter_by(sucursalid=data["sucursalid"], activo=True).update({"activo": False})

    template = Template_Balance(
        sucursalid=data["sucursalid"],
        nombre=data["nombre"],
        descripcion=data.get("descripcion"),
        clavepais=data.get("clavepais"),
        activo=data.get("activo", False)
    )

    db.session.add(template)
    db.session.commit()

    return jsonify({
        "message": "Template creado exitosamente",
        "template": {
            "templateid": template.templateid,
            "sucursalid": template.sucursalid,
            "nombre": template.nombre,
            "activo": template.activo
        }
    }), 201


# 📌 Actualizar un template balance
@template_balance_bp.route('/api/Updatetemplate', methods=['PUT'])
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
    template.clavepais = data.get("clavepais", template.clavepais)

    # Si se marca como activo, desactivar otros de la misma sucursal
    if data.get("activo") is not None:
        if data["activo"]:
            Template_Balance.query.filter(
                Template_Balance.sucursalid == template.sucursalid,
                Template_Balance.templateid != template.templateid,
                Template_Balance.activo == True
            ).update({"activo": False})
        template.activo = data["activo"]

    db.session.commit()

    return jsonify({
        "message": "Template actualizado exitosamente",
        "template": {
            "templateid": template.templateid,
            "sucursalid": template.sucursalid,
            "nombre": template.nombre,
            "activo": template.activo
        }
    })


# 📌 Listar todos los templates de una sucursal
@template_balance_bp.route('/api/Listtemplates', methods=['POST'])
def api_list_templates():
    data = request.get_json()
    if not data or "sucursalid" not in data:
        return jsonify({"error": "sucursalid es requerido"}), 400

    templates = Template_Balance.query.filter_by(sucursalid=data["sucursalid"]).all()

    return jsonify([
        {
            "templateid": t.templateid,
            "sucursalid": t.sucursalid,
            "nombre": t.nombre,
            "descripcion": t.descripcion,
            "clavepais": t.clavepais,
            "activo": t.activo,
            "created_at": t.created_at
        }
        for t in templates
    ])
