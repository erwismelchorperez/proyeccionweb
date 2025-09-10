from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField, IntegerField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from wtforms import SelectField

class IndicadorForm(FlaskForm):
    institutionid = SelectField('Institución', coerce=int, validators=[DataRequired()])
    grupoid = IntegerField('Grupo', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    numerador = StringField('Numerador', validators=[DataRequired()])
    numeradorctas = TextAreaField('Cuentas del Numerador', validators=[DataRequired()])
    denominador = StringField('Denominador', validators=[DataRequired()])
    denominadorctas = TextAreaField('Cuentas del Denominador', validators=[DataRequired()])
    
    submit = SubmitField('Guardar')
