from flask import Blueprint, request, jsonify
from app import db
from app.models import SucursalTemplate, Sucursal, Template_Balance

#sucursal_template_bp = Blueprint('sucursal_template_bp', __name__, url_prefix='/api/sucursal_template')
sucursal_template_bp = Blueprint('sucursal_template', __name__, template_folder='templates')

# Crear o actualizar
@sucursal_template_bp.route('/api/sucursal_template/create_or_update', methods=['POST'])
def create_or_update_sucursal_template():
    data = request.get_json()

    sucursalid = data.get('sucursalid')
    templateid = data.get('templateid')
    activo = data.get('activo', False)

    if not sucursalid or not templateid:
        return jsonify({"error": "sucursalid y templateid son requeridos"}), 400

    # Validar existencia de sucursal y template
    sucursal = Sucursal.query.get(sucursalid)
    if not sucursal:
        return jsonify({"error": "Sucursal no encontrada"}), 404

    template = Template_Balance.query.get(templateid)
    if not template:
        return jsonify({"error": "Template no encontrado"}), 404

    # Si activo=True, desactivar otros templates de la misma sucursal
    if activo:
        db.session.query(SucursalTemplate)\
            .filter(SucursalTemplate.sucursalid == sucursalid, SucursalTemplate.activo == True)\
            .update({"activo": False})

    # Verificar si ya existe la relación
    registro = SucursalTemplate.query.filter_by(sucursalid=sucursalid, templateid=templateid).first()
    if registro:
        registro.activo = activo
    else:
        registro = SucursalTemplate(sucursalid=sucursalid, templateid=templateid, activo=activo)
        db.session.add(registro)

    db.session.commit()
    return jsonify({"message": "Relación creada/actualizada exitosamente",
                    "suctempid": registro.suctempid,
                    "sucursalid": registro.sucursalid,
                    "templateid": registro.templateid,
                    "activo": registro.activo})
# Listar todos
@sucursal_template_bp.route('/api/sucursal_template/Listsucursal', methods=['GET'])
def listar_sucursal_template():
    registros = SucursalTemplate.query.all()
    return jsonify([
        {
            "suctempid": r.suctempid,
            "sucursalid": r.sucursalid,
            "templateid": r.templateid,
            "activo": r.activo
        } for r in registros
    ])
@sucursal_template_bp.route('/api/sucursal_template/list_by_sucursal', methods=['POST'])
def listar_por_sucursal_post():
    data = request.get_json()
    if not data or 'sucursalid' not in data:
        return jsonify({"error": "Se requiere el campo sucursalid"}), 400

    sucursalid = data['sucursalid']
    registros = SucursalTemplate.query.filter_by(sucursalid=sucursalid).all()

    return jsonify([
        {
            "suctempid": r.suctempid,
            "sucursalid": r.sucursalid,
            "templateid": r.templateid,
            "activo": r.activo
        } for r in registros
    ])
