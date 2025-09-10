from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Sucursal

sucursal_bp = Blueprint('sucursal', __name__, template_folder='templates')
@sucursal_bp.route('/api/Listsucursal', methods=['POST'])
def api_lista_sucursales():
    data = request.get_json()

    if not data or "institutionid" not in data:
        return jsonify({"error": "Debes enviar institutionid en el JSON"}), 400

    institution_id = data["institutionid"]

    sucursales = Sucursal.query.filter_by(institutionid=institution_id).all()
    print(sucursales)
    return jsonify([
        {
            "sucursalid": suc.sucursalid,
            "institutionid": suc.institutionid,
            "codigo": suc.codigo,
            "nombre": suc.nombre
        }
        for suc in sucursales
    ])
@sucursal_bp.route('/api/Createsucursal', methods=['POST'])
def api_crear_sucursal():
    data = request.get_json()

    # Validación básica (puedes mejorarla)
    if not data or "institutionid" not in data:
        return jsonify({"error": "institutionid es requerido"}), 400

    sucursal = Sucursal(
        institutionid=data.get("institutionid"),
        codigo=data.get("codigo"),
        nombre=data.get("nombre")
    )

    db.session.add(sucursal)
    db.session.commit()

    return jsonify({
        "message": "sucursal registrado exitosamente",
        "sucursal": {
            "sucursalid": sucursal.sucursalid,
            "institutionid": sucursal.institutionid,
            "codigo": sucursal.codigo,
            "nombre": sucursal.nombre
        }
    }), 201
@sucursal_bp.route('/api/Updatesucursal', methods=['POST'])
def api_update_sucursal():
    data = request.get_json()

    if not data or "sucursalid" not in data:
        return jsonify({"error": "sucursalid es requerido"}), 400

    # Obtener la sucursal a actualizar
    sucursal = Sucursal.query.get_or_404(data["sucursalid"])

    # Actualizar los campos si vienen en el JSON
    if "institutionid" in data:
        sucursal.institutionid = data["institutionid"]
    if "codigo" in data:
        sucursal.codigo = data["codigo"]
    if "nombre" in data:
        sucursal.nombre = data["nombre"]

    db.session.commit()

    return jsonify({
        "message": "Sucursal actualizada exitosamente",
        "sucursal": {
            "sucursalid": sucursal.sucursalid,
            "institutionid": sucursal.institutionid,
            "codigo": sucursal.codigo,
            "nombre": sucursal.nombre
        }
    }), 200

