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

class BalanceMensual(db.Model):
    __tablename__ = 'balancemensual'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    institucion_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.SmallInteger, nullable=False)  # SMALLINT se adapta a TINYINT
    nivel = db.Column(db.String(50))
    cuenta = db.Column(db.String(250))
    codigo = db.Column(db.String(10))
    saldo = db.Column(db.Numeric(10, 2))

    __table_args__ = (
        db.UniqueConstraint('institucion_id', 'anio', 'mes', name='uk_institucion_mes'),
    )

    # Relaciones opcionales
    institucion = db.relationship('Institution', backref=db.backref('balances_mensuales', lazy=True))
    usuario = db.relationship('User', backref=db.backref('balances_mensuales', lazy=True))

    def __repr__(self):
        return f"<BalanceMensual {self.anio}-{self.mes} Inst:{self.institucion_id} Saldo:{self.saldo}>"