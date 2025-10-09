from flask import Blueprint, request, jsonify
from app import db
from app.models import TipoCuenta

tipocuenta_bp = Blueprint('tipocuenta', __name__, template_folder='templates')
# Crear un nuevo tipo de cuenta
@tipocuenta_bp.route('/api/tipocuenta/create', methods=['POST'])
def create_tipocuenta():
    data = request.get_json()

    # Si el usuario envía un solo objeto, lo convertimos a lista
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        return jsonify({"error": "El cuerpo de la solicitud debe ser un objeto o una lista de objetos"}), 400

    created = []
    errors = []

    for item in data:
        clavetipo = item.get('clavetipo')
        nombre = item.get('nombre')

        # Validaciones
        if not nombre:
            errors.append({"item": item, "error": "El campo 'nombre' es requerido"})
            continue

        if TipoCuenta.query.filter_by(nombre=nombre).first():
            errors.append({"item": item, "error": "Ya existe un tipo de cuenta con ese nombre"})
            continue

        nuevo = TipoCuenta(clavetipo=clavetipo, nombre=nombre)
        db.session.add(nuevo)
        created.append(nuevo)

    # Solo hacemos commit si hay algo que crear
    if created:
        db.session.commit()

    return jsonify({
        "message": f"Se crearon {len(created)} tipo(s) de cuenta exitosamente",
        "creados": [
            {
                "tipocuentaid": tc.tipocuentaid,
                "clavetipo": tc.clavetipo,
                "nombre": tc.nombre
            }
            for tc in created
        ],
        "errores": errors
    }), 201 if created else 400
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
