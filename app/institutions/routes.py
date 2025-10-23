from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text, func
from app.models import Institution, TemplateBalance, ValidacionTemplate, Pais
from .forms import InstitutionForm, SubirTemplateForm, ValidacionTemplateForm
import requests

institutions_bp = Blueprint('institutions', __name__, template_folder='templates')

@institutions_bp.route('/instituciones')
def listar():
    instituciones = Institution.query.all()
    return render_template('institutions/listar.html', instituciones=instituciones)
@institutions_bp.route('/instituciones/nueva', methods=['GET', 'POST'])
def nueva():
    form = InstitutionForm()
    if form.validate_on_submit():
        nueva = Institution(nombre=form.nombre.data, descripcion=form.descripcion.data)
        db.session.add(nueva)
        db.session.commit()
        flash('Institución agregada correctamente.', 'success')
        return redirect(url_for('institutions.listar'))
    return render_template('institutions/formulario.html', form=form)
@institutions_bp.route('/instituciones/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    institucion = Institution.query.get_or_404(id)
    form = InstitutionForm(obj=institucion)
    if form.validate_on_submit():
        institucion.nombre = form.nombre.data
        institucion.descripcion = form.descripcion.data
        db.session.commit()
        flash('Institución actualizada.', 'success')
        return redirect(url_for('institutions.listar'))
    return render_template('institutions/formulario.html', form=form)
@institutions_bp.route('/instituciones/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    institucion = Institution.query.get_or_404(id)
    db.session.delete(institucion)
    db.session.commit()
    flash('Institución eliminada.', 'info')
    return redirect(url_for('institutions.listar'))
###### Apartado para subir archivo csv
@institutions_bp.route('/instituciones/subirtemplate/<int:id>', methods=['GET', 'POST'])
def subirtemplate(id):
    formTemplate = ValidacionTemplateForm()
    institucion = Institution.query.get_or_404(id)
    form = SubirTemplateForm()
    form.institucion.choices = [(i.id, i.nombre) for i in Institution.query.all()]
    form.institucion.data = institucion.id

    mostrar_formulario = True
    mostrar_validaciones = True
    templates = TemplateBalance.query.filter_by(institution_id=institucion.id).all()

    formTemplate.cuenta_objetivo.choices = [(t.codigo, f"{t.codigo} - {t.cuenta}") for t in templates]
    validaciones = ValidacionTemplate.query.filter_by(institucion_id=institucion.id).all()
    if templates:
        mostrar_formulario = False
    if validaciones:
        mostrar_validaciones = False

    if request.method == 'POST':
        if request.form.get('formulario') == 'template_form':
            nueva_validacion = ValidacionTemplate(
                institucion_id=id,
                descripcion=formTemplate.descripcion.data,
                cuenta_objetivo=formTemplate.cuenta_objetivo.data,
                expresion=formTemplate.expresion.data
            )
            db.session.add(nueva_validacion)
            db.session.commit()
            flash('Validación guardada correctamente.', 'success')
            return redirect(url_for('institutions.subirtemplate', id=id))
        
        elif form.validate_on_submit():
            archivo = form.archivo.data
            institucion_id = form.institucion.data

            # Leer el contenido del archivo directamente sin guardarlo
            stream = io.StringIO(archivo.stream.read().decode("utf-8-sig"))
            reader = csv.DictReader(stream)

            for row in reader:
                template = TemplateBalance(
                    nivel=row['nivel'],
                    cuenta=row['cuenta'],
                    codigo=row['codigo'].strip(),
                    proyeccion=row['proyeccion'].strip(),
                    institution_id=institucion_id
                )
                db.session.add(template)

            db.session.commit()
            flash('Template cargado directamente desde archivo en memoria.', 'success')
            return redirect(url_for('institutions.subirtemplate', id=institucion_id))

    return render_template('institutions/subirtemplate.html', form=form, institucion=institucion, templates=templates, mostrar_formulario=mostrar_formulario, mostrar_validaciones=mostrar_validaciones, validaciones=validaciones, formTemplate=formTemplate)
"""
    Apartado que regresará todo lo de postman en fomrato JSON
"""
@institutions_bp.route('/institucionesListar', methods=['GET','POST'])
def listarInstituciones():
    if request.method=='GET':
        institution_id=request.args.get("institutionid",type=int)
    else:
        data = request.get_json(silent=True) or {}
        institution_id = data.get('institutionid')
    # Si se pasa institutionid → filtra
    if institution_id:
        instituciones = Institution.query.filter_by(institutionid=institution_id).all()
    else:
        # Si no se pasa → devuelve todas
        instituciones = Institution.query.all()

    result = []
    for inst in instituciones:
        result.append({
            "id": inst.institutionid,
            "_id": inst._id,
            "alias": inst.alias,
            "nombre": inst.nombre,
            "descripcion": inst.descripcion,
            "clavepais": inst.country,
            "fecha_creacion": inst.fecha_creacion.isoformat() if inst.fecha_creacion else None
        })
    
    return jsonify(result)
@institutions_bp.route("/api/instituciones", methods=["GET"])
def obtener_empresas():
    try:
        # URL de la API externa
        url = "http://api-adminclient.rflatina.com/rfl/api/v1/companies"
        
        # Token Bearer
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjYyNDIwYTA4YjQzZTRjMDAxMzJkOGQxYiIsImVtYWlsIjoiaW5mb0ByZmxhdGluYS5jb20iLCJuYW1lIjoiR2FicmllbCIsImxhc3RfbmFtZSI6Ik1FZ3VleiIsImNvbXBhbnlfaWQiOiI2MDc2MmY5YTc2NmMwYTAwMWE5N2VjMjYiLCJjb21wYW55X25hbWUiOiJGcmllZHJpY2ggQ29uc3VsdGluZyBHcnVwIiwiY29tcGFueV9jb3VudHJ5IjoiTWV4aWNvIiwiY29tcGFueV9hbGlhcyI6IkZyaWVkcmljaCIsInJvbGUiOiJSaWVzZ28gQ3JlZGl0byIsIm1vZHVsZXMiOlsiYWxlLXJpZXNnb2RlY3LDqWRpdG8iLCJhbGUtZ2FwJ3MiLCJhbGUtYmVuY2htYXJraW5nIiwiYWxlLXRlbmRlbmNpYWRlcMOpcmRpZGEiLCJhbGUtbWF0cml6dHJhbnNpY2nDs24iLCJhbGUtY29zZWNoYXMiLCJhbGUtY29uY2VudHJhY2nDs24iLCJhbGUtbWF5b3Jlc2RldWRvcmVzIl0sImlhdCI6MTc2MDk4Njk0MCwiZXhwIjoxNzkyNTIyOTQwfQ.nGD7FkQWMNuXP-ofKd-Mh6LIi2TzTcplT6JEquZeIaI"  # ⚠️ remplázalo por tu token real
        
        # Encabezados de autorización
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        # Petición GET a la API externa
        response = requests.get(url, headers=headers, timeout=10)
        
        # Si la respuesta no fue exitosa, manejar error
        if response.status_code != 200:
            return jsonify({
                "error": f"Error al conectar con la API externa ({response.status_code})",
                "detalle": response.text
            }), response.status_code
        
        # Retornar la respuesta en formato JSON
        data = response.json()
        return jsonify({"message": "Datos obtenidos correctamente", "data": data})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@institutions_bp.route("/api/instituciones/unificar", methods=["GET"])
def obtener_empresas_header():
    try:
        # 1️⃣ Obtener token del header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Debe incluir 'Authorization' en los headers"}), 400

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "El header Authorization debe comenzar con 'Bearer '"}), 400

        token = auth_header.split(" ")[1]

        # 2️⃣ Consumir API externa
        url = "http://api-adminclient.rflatina.com/rfl/api/v1/companies"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return jsonify({
                "error": f"Error al conectar con la API externa ({response.status_code})",
                "detalle": response.text
            }), response.status_code

        companies = response.json()

        nuevos, actualizados, sin_cambios = 0, 0, 0

        for company in companies:
            company_id = company.get("_id")
            company_name = company.get("company_name")
            company_alias = company.get("alias")
            country_name = company.get("company_country")

            if not company_id:
                continue

            # 3️⃣ Buscar clave del país
            clavepais = None
            if country_name:
                pais = Pais.query.filter(func.lower(Pais.nombre) == country_name.lower()).first()
                if pais:
                    clavepais = pais.clavepais

            existe = Institution.query.filter_by(_id=company_id).first()

            if not existe:
                # 🆕 Crear nuevo registro
                nueva_inst = Institution(
                    _id=company_id,
                    nombre=company_name,
                    alias=company_alias,
                    country=clavepais
                )
                db.session.add(nueva_inst)
                nuevos += 1
            else:
                # 🔄 Verificar si cambió algo
                cambios = False
                if existe.nombre != company_name:
                    existe.nombre = company_name
                    cambios = True
                if existe.alias != company_alias:
                    existe.alias = company_alias
                    cambios = True
                if existe.country != clavepais:
                    existe.country = clavepais
                    cambios = True

                if cambios:
                    actualizados += 1
                else:
                    sin_cambios += 1

        db.session.commit()

        # 4️⃣ Resumen final
        return jsonify({
            "message": "Sincronización completada",
            "nuevos": nuevos,
            "actualizados": actualizados,
            "sin_cambios": sin_cambios,
            "total_recibidos": len(companies)
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error al realizar la solicitud externa", "detalle": str(e)}), 500

    except Exception as e:
        # Cualquier otro error inesperado
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500
