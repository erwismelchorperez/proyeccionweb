from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField, SelectField, IntegerField, DecimalField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from wtforms import SelectField
from wtforms.validators import DataRequired, NumberRange, Regexp

class BalanceForm(FlaskForm):
    institucion_id = SelectField('Institución', coerce=int, validators=[DataRequired()])
    anio = IntegerField('Año', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    mes = IntegerField('Mes', validators=[DataRequired(), NumberRange(min=1, max=12)])
    nivel = StringField('Nivel')
    cuenta = StringField('Cuenta')
    codigo = StringField('Código')
    saldo = DecimalField('Saldo', validators=[DataRequired()])
    submit = SubmitField('Guardar')