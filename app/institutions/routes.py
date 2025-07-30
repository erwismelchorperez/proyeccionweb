from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Institution
from .forms import InstitutionForm

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