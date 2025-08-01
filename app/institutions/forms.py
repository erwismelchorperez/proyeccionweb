from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
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