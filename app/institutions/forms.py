from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from wtforms import SelectField

class InstitutionForm(FlaskForm):
    nombre = StringField('Nombre de la Institución', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    submit = SubmitField('Guardar')

class SubirTemplateForm(FlaskForm):
    institucion = SelectField('Institución', coerce=int)
    archivo = FileField('Archivo CSV', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Solo archivos CSV.')
    ])

class ValidacionTemplateForm(FlaskForm):
    formulario = HiddenField(default='template_form')
    institucion_id = SelectField('Institución', coerce=int)
    descripcion = StringField('Descripción')
    cuenta_objetivo = SelectField('Cuenta Objetivo', coerce=str)
    expresion = StringField('Expresión', validators=[DataRequired()])