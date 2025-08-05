from . import auth_bp  # Importa el blueprint definido en __init__.py

from flask import render_template, redirect, url_for, flash, request
from .forms import LoginForm, RegisterForm
from ..models import db, User, Institution
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Sesión iniciada correctamente.', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    print("                 Registro de usuarios")
    form = RegisterForm()
    form.institution_id.choices = [(0, 'Seleccione una institución')] + [(i.id, i.nombre) for i in Institution.query.all()]
    print("   Validation                ",form.validate_on_submit())
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, name=form.name.data, lastname= form.lastname.data, email=form.email.data, password=hashed_pw, institution_id=form.institution_id.data)
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.usuarios'))
    else:
        print(form.errors)  # <-- esto te dice qué campos fallaron y por qué
    return render_template('auth/register.html', form=form)

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('auth/dashboard.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))



@auth_bp.route('/usuarios')
def usuarios():
    usuarios = User.query.all()
    return render_template('auth/usuarios.html', usuarios=usuarios)
@auth_bp.route('/auth/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    usuario = User.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado.', 'info')
    return redirect(url_for('auth.usuarios'))
@auth_bp.route('/auth/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    usuario = User.query.get_or_404(id)
    form = RegisterForm(obj=usuario)
    form.institution_id.choices = [(0, 'Seleccione una institución')] + [(i.id, i.nombre) for i in Institution.query.all()]
    form.institution_id.data = usuario.institution_id
    # Establecer el valor seleccionado si es GET
    print(form.institution_id.data)
    print(usuario.institution_id)
    
    if form.validate_on_submit():
        
        usuario.username = form.username.data
        usuario.name = form.name.data
        usuario.lastname = form.lastname.data
        usuario.email = form.email.data
        usuario.institution_id = form.institution_id.data

        #Si el campo de contraseña no está vacío, actualiza
        if form.password.data:
            usuario.password = generate_password_hash(form.password.data)

        db.session.commit()
        flash('Usuario actualizado.', 'success')
        return redirect(url_for('auth.usuarios'))
    return render_template('auth/register.html', form=form)
