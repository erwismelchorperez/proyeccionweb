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
