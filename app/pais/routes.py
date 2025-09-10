from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Pais

pais_bp = Blueprint('pais', __name__, template_folder='templates')
@pais_bp.route('/api/Listpais', methods=['GET'])
def api_lista_paises():
    countries = Pais.query.all()
    return jsonify([
        {
            "clavepais": pais.clavepais,
            "nombrepais": pais.nombrepais
        }
        for pais in countries
    ])