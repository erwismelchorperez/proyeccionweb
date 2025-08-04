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
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, name=form.name.data, lastname= form.lastname.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.usuarios'))
    return render_template('auth/usuarios.html', form=form)

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('auth/dashboard.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))



@auth_bp.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
    form = RegisterForm()
    usuarios = User.query.all()
    # Cargar instituciones de la base de datos
    institutions = Institution.query.all()
    form.institution_id.choices = [(inst.id, inst.nombre) for inst in institutions]


    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        nuevo_usuario = User(
            username=form.username.data,
            name=form.name.data,
            lastname=form.lastname.data,
            email=form.email.data,
            password=hashed_pw
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario registrado exitosamente.', 'success')
        return redirect(url_for('auth.usuarios'))

    return render_template('auth/usuarios.html', form=form, usuarios=usuarios)

@auth_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = RegisterForm(obj=user)

    # Cargar las instituciones disponibles al combo box
    form.institution_id.choices = [(i.id, i.name) for i in Institution.query.all()]

    if form.validate_on_submit():
        # Actualizar los campos desde el formulario
        user.name = form.name.data
        user.lastname = form.lastname.data
        user.username = form.username.data
        user.email = form.email.data
        user.institution_id = form.institution_id.data

        if form.password.data:  # Solo actualiza si el campo no está vacío
            user.password = generate_password_hash(form.password.data)

        db.session.commit()
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('auth.usuarios'))

    # Cargar valores actuales si GET
    return render_template('auth/edit_user.html', form=form, user=user)