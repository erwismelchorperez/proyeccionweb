from flask import Blueprint, request, jsonify
from app import db
from app.models import TipoCuenta

tipocuenta_bp = Blueprint('tipocuenta', __name__, template_folder='templates')
# Crear un nuevo tipo de cuenta
@tipocuenta_bp.route('/api/tipocuenta/create', methods=['POST'])
def create_tipocuenta():
    data = request.get_json()
    clavetipo = data.get('clavetipo')
    nombre = data.get('nombre')

    if not nombre:
        return jsonify({"error": "El campo 'nombre' es requerido"}), 400

    # Validar que el nombre sea único
    if TipoCuenta.query.filter_by(nombre=nombre).first():
        return jsonify({"error": "Ya existe un tipo de cuenta con ese nombre"}), 400

    nuevo = TipoCuenta(clavetipo=clavetipo, nombre=nombre)
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({
        "message": "Tipo de cuenta creado exitosamente",
        "tipocuentaid": nuevo.tipocuentaid,
        "clavetipo": nuevo.clavetipo,
        "nombre": nuevo.nombre
    }), 201
# Listar todos los tipos de cuenta
@tipocuenta_bp.route('/api/tipocuenta/list', methods=['GET'])
def list_tipocuentas():
    registros = TipoCuenta.query.all()
    return jsonify([
        {
            "tipocuentaid": r.tipocuentaid,
            "clavetipo": r.clavetipo,
            "nombre": r.nombre
        } for r in registros
    ])
# Actualizar un tipo de cuenta
@tipocuenta_bp.route('/api/tipocuenta/update/<int:tipocuentaid>', methods=['PUT'])
def update_tipocuenta(tipocuentaid):
    data = request.get_json()
    registro = TipoCuenta.query.get(tipocuentaid)

    if not registro:
        return jsonify({"error": "Tipo de cuenta no encontrado"}), 404

    # Actualizar solo los campos enviados
    registro.clavetipo = data.get('clavetipo', registro.clavetipo)
    registro.nombre = data.get('nombre', registro.nombre)

    db.session.commit()

    return jsonify({
        "message": "Tipo de cuenta actualizado exitosamente",
        "tipocuentaid": registro.tipocuentaid,
        "clavetipo": registro.clavetipo,
        "nombre": registro.nombre
    })
