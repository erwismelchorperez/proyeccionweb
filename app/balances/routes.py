from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from app.models import Institution, TemplateBalance, ValidacionTemplate, BalanceMensual
from .forms import BalanceForm
from flask_login import current_user

balances_bp = Blueprint('balances', __name__, template_folder='templates')
###### Apartado para subir archivo csv
@balances_bp.route('/balances')
def listar():
    balances = BalanceMensual.query.all()
    print(current_user.username, "          ", current_user.id)
    return render_template('balances/listar.html', balances=balances, usuariologeado = current_user)

