from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Institution, TemplateBalance, ValidacionTemplate
from .forms import InstitutionForm, SubirTemplateForm, ValidacionTemplateForm

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
@institutions_bp.route('/institucionesListar')
def listarInstituciones():
    instituciones = Institution.query.all()
    
    # Convertir cada objeto a diccionario
    result = []
    for inst in instituciones:
        result.append({
            "id": inst.id,
            "nombre": inst.nombre,
            "descripcion": inst.descripcion,
            "fecha_creacion": inst.fecha_creacion.isoformat() if inst.fecha_creacion else None
        })
    
    return jsonify(result)
@institutions_bp.route('/instituciones/CrearInstitucion', methods=['POST'])
def CrearInstitucion():
    data = request.get_json()  # recibe JSON desde el front o Postman
    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400

    nombre = data.get("nombre")
    descripcion = data.get("descripcion")

    if not nombre:  # validación simple
        return jsonify({"error": "El nombre es obligatorio"}), 400

    nueva_inst = Institution(nombre=nombre, descripcion=descripcion)
    db.session.add(nueva_inst)
    db.session.commit()

    # Devolver el objeto creado como JSON
    return jsonify({
        "id": nueva_inst.id,
        "nombre": nueva_inst.nombre,
        "descripcion": nueva_inst.descripcion,
        "fecha_creacion": nueva_inst.fecha_creacion.isoformat() if nueva_inst.fecha_creacion else None
    }), 201
@institutions_bp.route('/instituciones/subirTemplate', methods=['GET', 'POST'])
def subirTemplate():
    # 1. Verifica que venga el id en el form-data
    institucion_id = request.form.get('institucion_id')
    if not institucion_id:
        return jsonify({
            "status": "error",
            "message": "Debes enviar el campo 'institucion_id' en el form-data."
        }), 400

    institucion = Institution.query.get(institucion_id)
    if not institucion:
        return jsonify({
            "status": "error",
            "message": f"No existe la institución con id {institucion_id}."
        }), 404

    # 2. Verifica que venga un archivo
    if 'archivo' not in request.files:
        return jsonify({
            "status": "error",
            "message": "No se encontró el archivo CSV en la petición (usa form-data con key='archivo')."
        }), 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({
            "status": "error",
            "message": "El archivo CSV está vacío."
        }), 400

    try:
        # 3. Leer CSV directamente en memoria
        stream = io.StringIO(archivo.stream.read().decode("utf-8-sig"))
        reader = csv.DictReader(stream)

        nuevos_templates = []
        for row in reader:
            template = TemplateBalance(
                nivel=row['nivel'],
                cuenta=row['cuenta'],
                codigo=row['codigo'].strip(),
                proyeccion=row['proyeccion'].strip(),
                institution_id=institucion.id
            )
            db.session.add(template)
            nuevos_templates.append({
                "nivel": row['nivel'],
                "cuenta": row['cuenta'],
                "codigo": row['codigo'].strip(),
                "proyeccion": row['proyeccion'].strip()
            })

        db.session.commit()

        # 4. Respuesta JSON para Postman
        return jsonify({
            "status": "success",
            "message": f"Se cargaron {len(nuevos_templates)} registros desde el archivo CSV.",
            "templates_guardados": nuevos_templates
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error procesando el CSV: {str(e)}"
        }), 500
@institutions_bp.route('/validaciones/listarAllValidaciones', methods=['POST'])
def listarAllValidaciones():
    # Obtener el id de la institución desde form-data
    institucion_id = request.form.get('institucion_id')

    if not institucion_id:
        return jsonify({
            "status": "error",
            "message": "Debes enviar 'institucion_id' en el form-data."
        }), 400

    institucion = Institution.query.get(institucion_id)
    if not institucion:
        return jsonify({
            "status": "error",
            "message": f"No existe la institución con id {institucion_id}."
        }), 404

    # Filtrar validaciones de esa institución
    validaciones = ValidacionTemplate.query.filter_by(institucion_id=institucion_id).all()

    # Convertir cada objeto a diccionario
    result = []
    for v in validaciones:
        result.append({
            "id": v.id,
            "institucion_id": v.institucion_id,
            "descripcion": v.descripcion,
            "cuenta_objetivo": v.cuenta_objetivo,
            "expresion": v.expresion
        })

    return jsonify({
        "status": "success",
        "institucion_id": institucion_id,
        "validaciones": result
    }), 200
@institutions_bp.route('/validaciones/InsertAllValidaciones', methods=['POST'])
def InsertAllValidaciones():
    # Obtener el id de la institución desde form-data o JSON
    institucion_id = request.form.get('institucion_id') or request.json.get('institucion_id')
    if not institucion_id:
        return jsonify({"status": "error", "message": "Debes enviar 'institucion_id'"}), 400

    institucion = Institution.query.get(institucion_id)
    if not institucion:
        return jsonify({"status": "error", "message": f"No existe la institución con id {institucion_id}"}), 404

    try:
        # Ejecutar la función de PostgreSQL
        resultado = db.session.execute(text("SELECT * from generarvalidaciones(:val)"), {"val": institucion_id})
        valor_resultado = resultado.fetchone()[0]

        return jsonify({
            "status": "success",
            "institucion_id": institucion_id,
            "resultado": valor_resultado
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
"""
    Apartado que regresará todo lo de postman en fomrato JSON
"""