from . import auth_bp  # Importa el blueprint definido en __init__.py

from flask import render_template, redirect, url_for, flash, request
from .forms import LoginForm, RegisterForm
from ..models import db, User
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
        return redirect(url_for('auth.login'))
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
