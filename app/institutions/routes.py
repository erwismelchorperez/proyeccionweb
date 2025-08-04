from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
import io
import csv
from werkzeug.utils import secure_filename
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