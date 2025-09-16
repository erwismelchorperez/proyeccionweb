from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    lastname = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default='usuario')  # puede ser 'admin' o 'usuario'

    institution_id = db.Column(db.Integer, db.ForeignKey('institution.institutionid'), nullable=False)
class Institution(db.Model):
    institutionid = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())

    usuarios = db.relationship('User', backref='institution', lazy=True, cascade="all, delete")
    
    def __repr__(self):
        return f"<Institution {self.nombre}>"
class Sucursal(db.Model):
    __tablename__ = "sucursal"

    sucursalid = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    institutionid = db.Column(db.Integer, db.ForeignKey('institution.institutionid'), nullable=False)
    institution = db.relationship('Institution', backref=db.backref('sucursal', lazy=True))

    def __repr__(self):
        return f"<Sucursal {self.nombre} ({self.codigo})>"
class SucursalTemplate(db.Model):
    """
        Esta tabla mantiene la relación entre sucursal y template
    """
    __tablename__ = 'sucursal_template'
    
    suctempid = db.Column(db.Integer, primary_key=True)
    sucursalid = db.Column(db.Integer, db.ForeignKey('sucursal.sucursalid', ondelete='CASCADE'), nullable=False)
    templateid = db.Column(db.Integer, db.ForeignKey('template_balance.templateid', ondelete='CASCADE'), nullable=False)
    activo = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (db.UniqueConstraint('sucursalid', 'templateid', name='uq_sucursal_template'),)
class Template_Balance(db.Model):
    __tablename__ = 'template_balance'
    templateid = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Template_Balance {self.nombre}>"
class CuentaContable(db.Model):
    __tablename__ = 'cuenta_contable'

    cuentaid = db.Column(db.Integer, primary_key=True)
    templateid = db.Column(db.Integer, db.ForeignKey('template_balance.templateid'), nullable=False)
    nivel = db.Column(db.Integer)
    tipoid = db.Column(db.Integer, db.ForeignKey('tipocuenta.tipocuentaid'), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    proyeccion = db.Column(db.String(2))
    segmento = db.Column(db.String(150))
    tipocuenta = db.relationship('TipoCuenta', backref=db.backref('cuenta_contable', lazy=True))

    def __repr__(self):
        return f"<CuentaContable {self.codigo} - {self.nombre}>"
class SaldoMensualCTS(db.Model):
    __tablename__ = 'saldo_mensual_cts'

    saldoctsid = db.Column(db.Integer, primary_key=True)
    cuentaid = db.Column(db.Integer, db.ForeignKey('cuenta_contable.cuentaid'), nullable=False)
    periodoid = db.Column(db.Integer, db.ForeignKey('periodo.periodoid'), nullable=False)
    saldo = db.Column(db.Numeric(18, 2))

    def __repr__(self):
        return f"<SaldoMensualCTS {self.anio}-{self.mes} cuenta={self.cuentaid}>"
class TipoCuenta(db.Model):
    __tablename__ = 'tipocuenta'
    tipocuentaid = db.Column(db.Integer, primary_key=True)
    clavetipo = db.Column(db.String(2))
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<TipoCuenta {self.tipocuentaid} - {self.nombre}>"
class Variable(db.Model):
    __tablename__ = 'variables'

    variableid = db.Column(db.Integer, primary_key=True)
    nombrevariable = db.Column(db.String(100), nullable=False)
    descripcionvariable = db.Column(db.Text)
    clavepais = db.Column(db.String(2), db.ForeignKey('pais.clavepais'))

    # Relación opcional si ya tienes el modelo País
    pais = db.relationship('Pais', backref=db.backref('variables', lazy=True))

    def __repr__(self):
        return f"<Variable {self.nombrevariable}>"
class ValorVariable(db.Model):
    __tablename__ = 'valor_variable'

    valorvariableid = db.Column(db.Integer, primary_key=True)
    variableid = db.Column(db.Integer, db.ForeignKey('variables.variableid', ondelete='CASCADE'),nullable=False)
    periodoid = db.Column(db.Integer,db.ForeignKey('periodo.periodoid'),nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=True)

    def __repr__(self):
        return f"<ValorVariable {self.valorvariableid}>"
class TempVar(db.Model):
    __tablename__ = 'tempvar'
    templateid = db.Column(db.Integer, db.ForeignKey('template_balance.templateid'),primary_key=True)
    variableid = db.Column(db.Integer, db.ForeignKey('variables.variableid'), primary_key=True)

    def __repr__(self):
        return f"<TempVar templateid={self.templateid}, variableid={self.variableid}>"
class Indicador(db.Model):
    __tablename__ = 'indicador'

    indicadorid = db.Column(db.Integer, primary_key=True)
    grupoid = db.Column(db.Integer, db.ForeignKey('grupo.grupoid', ondelete='CASCADE'), nullable=False)
    clavepais = db.Column(db.String(2), db.ForeignKey('pais.clavepais'))
    indicador = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    formula = db.Column(JSONB)

    grupo = db.relationship('Grupo', backref=db.backref('indicador', lazy=True))

    def __repr__(self):
        return f"<Indicador {self.indicador}>"
class TempInd(db.Model):
    __tablename__ = 'tempind'
    indicadorid = db.Column(db.Integer, db.ForeignKey('indicador.indicadorid'),primary_key=True)
    templateid = db.Column(db.Integer, db.ForeignKey('template_balance.templateid'), primary_key=True)
    formula = db.Column(JSONB)  # <-- Columna para guardar JSON

    def __repr__(self):
        return f"<TempVar templateid={self.templateid}, templateid={self.templateid}>"
class ValorIndicador(db.Model):
    __tablename__ = 'valorindicador'

    valorindid = db.Column(db.Integer, primary_key=True)
    indicadorid = db.Column(db.Integer, db.ForeignKey('indicador.indicadorid'), nullable=False)
    periodoid = db.Column(db.Integer, db.ForeignKey('periodo.periodoid'), nullable=False)
    valor = db.Column(db.Numeric(18,2))

    __table_args__ = (
        db.UniqueConstraint('indicadorid', 'periodoid', name='uq_indicador_periodo'),
    )

    def __repr__(self):
        return f"<ValorIndicador {self.indicadorid} - {self.periodoid} - {self.valor}>"
class Modelo(db.Model):
    __tablename__ = 'modelos'

    modeloid = db.Column(db.Integer, primary_key=True)
    cuentaid = db.Column(db.Integer, db.ForeignKey('cuenta_contable.cuentaid'), nullable=False)
    modelo = db.Column(db.String(100))
    ubicacion = db.Column(db.String(250))
    variables = db.Column(JSONB)  # <-- Columna para guardar JSON

    cuenta = db.relationship('CuentaContable', backref=db.backref('modelos', lazy=True))

    def __repr__(self):
        return f"<Modelo {self.modeloid} - {self.modelo}>"
class Prediccion(db.Model):
    __tablename__ = 'predicciones'

    prediccionid = db.Column(db.Integer, primary_key=True)
    modeloid = db.Column(db.Integer, db.ForeignKey('modelos.modeloid'), nullable=False)
    periodoid = db.Column(db.Integer, db.ForeignKey('periodo.periodoid'), nullable=False)
    prediccion = db.Column(db.Numeric(18,2))

    modelo = db.relationship('Modelo', backref=db.backref('predicciones', lazy=True))

    def __repr__(self):
        return f"<Prediccion {self.prediccionid} - Modelo {self.modeloid} - Periodo {self.periodoid}>"
"""
    Apartado de catálogos
        Periodo
        Segmento de cuenta
        Tipo de cuenta
        País
"""
class Periodo(db.Model):    
    __tablename__ = 'periodo'

    periodoid = db.Column(db.Integer, primary_key=True)
    anio      = db.Column(db.Integer, nullable=False)
    mes       = db.Column(db.Integer, nullable=False)

    # Garantiza que (anio, mes) sea único, igual que en el SQL
    __table_args__ = (
        db.UniqueConstraint('anio', 'mes', name='uq_periodo_anio_mes'),
    )

    def __repr__(self):
        return f"<Periodo {self.anio}-{self.mes}>"
class Pais(db.Model):
    __tablename__ = "pais"

    clavepais = db.Column(db.String(2), primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"<Pais {self.nombre}>"
class Grupo(db.Model):
    __tablename__ = 'grupo'

    grupoid = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Grupo {self.nombre}>"
"""
    Apartado superior
    Primera parte del proyecto
"""
class TemplateBalance(db.Model):
    __tablename__ = 'templateBalance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # si quieres agregar un id único
    nivel = db.Column(db.String(50))
    cuenta = db.Column(db.String(50))
    codigo = db.Column(db.String(10))
    proyeccion = db.Column(db.String(2))
    #fechacierre = db.Column(db.Date)
    #institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))

    # Relación inversa, opcional (si quieres acceder a la institución desde este modelo)
    #institution = db.relationship('Institution', backref=db.backref('balances', lazy=True))
class ValidacionTemplate(db.Model):
    __tablename__ = 'validaciones_template'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #institucion_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    cuenta_objetivo = db.Column(db.String(50), nullable=False)
    expresion = db.Column(db.String(100), nullable=False)  # Ej: '+5+6+7'
    operador = db.Column(db.String(5), default='=')
    activo = db.Column(db.Boolean, default=True)

    #institucion = db.relationship('Institution', backref=db.backref('validaciones', lazy=True, cascade='all, delete'))

    def __repr__(self):
        return f"<ValidacionTemplate {self.descripcion}>"
class Indicadores(db.Model):
    __tablename__ = 'indicadores'

    indicadorid = db.Column(db.Integer, primary_key=True)  # SERIAL en Postgres → Integer + PK
    #institutionid = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    grupoid = db.Column(db.Integer, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    numerador = db.Column(db.String(150), nullable=True)
    numeradorctas = db.Column(db.Text, nullable=True)
    denominador = db.Column(db.String(150), nullable=True)
    denominadorctas = db.Column(db.Text, nullable=True)

    # Relación con Institution
    #institution = db.relationship('Institution', backref=db.backref('indicadores', lazy=True))

    def __repr__(self):
        return f"<Indicadores {self.descripcion}>"
class BalanceMensual(db.Model):
    __tablename__ = 'balancemensual'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    #institucion_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.SmallInteger, nullable=False)  # SMALLINT se adapta a TINYINT
    nivel = db.Column(db.String(50))
    cuenta = db.Column(db.String(250))
    codigo = db.Column(db.String(10))
    saldo = db.Column(db.Numeric(10, 2))

    #__table_args__ = (db.UniqueConstraint('institucion_id', 'anio', 'mes', name='uk_institucion_mes'),)

    # Relaciones opcionales
    #institucion = db.relationship('Institution', backref=db.backref('balances_mensuales', lazy=True))
    usuario = db.relationship('User', backref=db.backref('balances_mensuales', lazy=True))

    def __repr__(self):
        return f"<BalanceMensual {self.anio}-{self.mes} Inst:{self.institucion_id} Saldo:{self.saldo}>"

