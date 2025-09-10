from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    lastname = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default='usuario')  # puede ser 'admin' o 'usuario'

    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())

    usuarios = db.relationship('User', backref='institution', lazy=True, cascade="all, delete")
    
    def __repr__(self):
        return f"<Institution {self.nombre}>"

class TemplateBalance(db.Model):
    __tablename__ = 'templateBalance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # si quieres agregar un id único
    nivel = db.Column(db.String(50))
    cuenta = db.Column(db.String(50))
    codigo = db.Column(db.String(10))
    proyeccion = db.Column(db.String(2))
    #fechacierre = db.Column(db.Date)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))

    # Relación inversa, opcional (si quieres acceder a la institución desde este modelo)
    institution = db.relationship('Institution', backref=db.backref('balances', lazy=True))

class ValidacionTemplate(db.Model):
    __tablename__ = 'validaciones_template'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    institucion_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    cuenta_objetivo = db.Column(db.String(50), nullable=False)
    expresion = db.Column(db.String(100), nullable=False)  # Ej: '+5+6+7'
    operador = db.Column(db.String(5), default='=')
    activo = db.Column(db.Boolean, default=True)

    institucion = db.relationship('Institution', backref=db.backref('validaciones', lazy=True, cascade='all, delete'))

    def __repr__(self):
        return f"<ValidacionTemplate {self.descripcion}>"

class Indicador(db.Model):
    __tablename__ = 'indicadores'

    indicadorid = db.Column(db.Integer, primary_key=True)  # SERIAL en Postgres → Integer + PK
    institutionid = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    grupoid = db.Column(db.Integer, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    numerador = db.Column(db.String(150), nullable=True)
    numeradorctas = db.Column(db.Text, nullable=True)
    denominador = db.Column(db.String(150), nullable=True)
    denominadorctas = db.Column(db.Text, nullable=True)

    # Relación con Institution
    institution = db.relationship('Institution', backref=db.backref('indicadores', lazy=True))

    def __repr__(self):
        return f"<Indicador {self.descripcion}>"

class Pais(db.Model):
    __tablename__ = "pais"

    clavepais = db.Column(db.String(2), primary_key=True)
    nombrepais = db.Column(db.String(150), nullable=False)

    # Relación con instituciones (un país puede tener muchas instituciones)
    #instituciones = db.relationship('Institution', backref='pais', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Pais {self.nombre}>"

class Sucursal(db.Model):
    __tablename__ = "sucursal"

    sucursalid = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    institutionid = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)

    # Relación: una sucursal pertenece a una institución
    institution = db.relationship('Institution', backref=db.backref('sucursal', lazy=True))

    def __repr__(self):
        return f"<Sucursal {self.nombre} ({self.codigo})>"
class Template_Balance(db.Model):
    __tablename__ = 'template_balance'

    templateid = db.Column(db.Integer, primary_key=True)
    sucursalid = db.Column(db.Integer, db.ForeignKey('sucursal.sucursalid'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.String(250), nullable=True)
    clavepais = db.Column(db.String(2), db.ForeignKey('pais.clavepais'), nullable=True)
    activo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relaciones
    sucursal = db.relationship('Sucursal', backref=db.backref('templates', lazy=True))
    pais = db.relationship('Pais', backref=db.backref('templates', lazy=True))

    def __repr__(self):
        return f"<Template_Balance {self.nombre}>"
class CuentaContable(db.Model):
    __tablename__ = 'cuenta_contable'

    cuentaid = db.Column(db.Integer, primary_key=True)
    templateid = db.Column(db.Integer, db.ForeignKey('template_balance.templateid'), nullable=False)
    nivel = db.Column(db.Integer)
    tipo = db.Column(db.String(50))
    codigo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    proyeccion = db.Column(db.String(2))
    segmento = db.Column(db.String(50))

    def __repr__(self):
        return f"<CuentaContable {self.codigo} - {self.nombre}>"
class SaldoMensualCTS(db.Model):
    __tablename__ = 'saldo_mensual_cts'

    saldoctsid = db.Column(db.Integer, primary_key=True)
    cuentaid = db.Column(db.Integer, db.ForeignKey('cuenta_contable.cuentaid'), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    saldo = db.Column(db.Numeric(18, 2))

    def __repr__(self):
        return f"<SaldoMensualCTS {self.anio}-{self.mes} cuenta={self.cuentaid}>"


