from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')
class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    lastname = StringField('Apellidos', validators=[DataRequired()])
    email = StringField('Correo', validators=[Email(), DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    #confirm = PasswordField('Confirmar Contraseña', validators=[EqualTo('password')])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir')])
    submit = SubmitField('Registrarse')