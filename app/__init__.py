from flask import Flask, redirect, url_for
from config import Config
from .models import db, User
from flask_login import LoginManager
from flask_login import current_user

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar base de datos y login manager
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Registrar blueprint
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.institutions.routes import institutions_bp
    app.register_blueprint(institutions_bp)

    from app.indicadores.routes import indicadores_bp
    app.register_blueprint(indicadores_bp)

    from app.pais.routes import pais_bp
    app.register_blueprint(pais_bp)

    from app.sucursal.routes import sucursal_bp
    app.register_blueprint(sucursal_bp)

    from app.template_Balance.routes import template_balance_bp
    app.register_blueprint(template_balance_bp)

    from app.cuentacontable.routes import cuentacontable_bp
    app.register_blueprint(cuentacontable_bp)

    from app.saldomensual.routes import saldo_mensual_cts_bp
    app.register_blueprint(saldo_mensual_cts_bp)

    from app.periodos.routes import periodo_bp
    app.register_blueprint(periodo_bp)

    from app.sucursaltemplate.routes import sucursal_template_bp
    app.register_blueprint(sucursal_template_bp)

    from app.tipocuenta.routes import tipocuenta_bp
    app.register_blueprint(tipocuenta_bp)

    from app.variables.routes import variables_bp
    app.register_blueprint(variables_bp)

    from app.valorvariable.routes import valorvariable_bp
    app.register_blueprint(valorvariable_bp)

    from app.tempvar.routes import tempvar_bp
    app.register_blueprint(tempvar_bp)

    from app.grupo.routes import grupo_bp
    app.register_blueprint(grupo_bp)

    from app.indicador.routes import indicador_bp
    app.register_blueprint(indicador_bp)

    from app.tempind.routes import tempind_bp
    app.register_blueprint(tempind_bp)

    from app.valorindicador.routes import valorindicador_bp
    app.register_blueprint(valorindicador_bp)

    from app.modelos.routes import modelos_bp
    app.register_blueprint(modelos_bp)

    from app.prediccion.routes import predicciones_bp
    app.register_blueprint(predicciones_bp)

    from app.escenarios.routes import escenario_bp
    app.register_blueprint(escenario_bp)

    from app.escenariocuenta.routes import escenariocuenta_bp
    app.register_blueprint(escenariocuenta_bp)

    from app.balances.routes import balances_bp
    app.register_blueprint(balances_bp)


    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('auth.dashboard'))
        return redirect(url_for('auth.login'))

    # loader de usuario
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
