from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Institution, Indicador, TemplateBalance
from .forms import IndicadorForm

indicadores_bp = Blueprint('indicador', __name__, template_folder='templates')

@indicadores_bp.route('/indicadores/crear', methods=['GET', 'POST'])
def crear_indicador():
    form = IndicadorForm()
    # llenar el select con instituciones
    form.institutionid.choices = [(i.id, i.nombre) for i in Institution.query.all()]

    if form.validate_on_submit():
        indicador = Indicador(
            institutionid=form.institutionid.data,
            grupoid=form.grupoid.data,
            descripcion=form.descripcion.data,
            numerador=form.numerador.data,
            numeradorctas=form.numeradorctas.data,
            denominador=form.denominador.data,
            denominadorctas=form.denominadorctas.data
        )
        db.session.add(indicador)
        db.session.commit()
        flash('Indicador registrado exitosamente', 'success')
        return redirect(url_for('lista_indicadores'))
    
    return render_template('indicadores/crear.html', form=form)
@indicadores_bp.route('/api/Createindicadores', methods=['POST'])
def api_crear_indicador():
    data = request.get_json()

    # Validación básica (puedes mejorarla)
    if not data or "institutionid" not in data:
        return jsonify({"error": "institutionid es requerido"}), 400

    indicador = Indicador(
        institutionid=data.get("institutionid"),
        grupoid=data.get("grupoid"),
        descripcion=data.get("descripcion"),
        numerador=data.get("numerador"),
        numeradorctas=data.get("numeradorctas"),  # lista JSON -> ARRAY en PostgreSQL
        denominador=data.get("denominador"),
        denominadorctas=data.get("denominadorctas")  # lista JSON -> ARRAY en PostgreSQL
    )

    db.session.add(indicador)
    db.session.commit()

    return jsonify({
        "message": "Indicador registrado exitosamente",
        "indicador": {
            "id": indicador.indicadorid,
            "institutionid": indicador.institutionid,
            "grupoid": indicador.grupoid,
            "descripcion": indicador.descripcion,
            "numerador": indicador.numerador,
            "numeradorctas": indicador.numeradorctas,
            "denominador": indicador.denominador,
            "denominadorctas": indicador.denominadorctas
        }
    }), 201
@indicadores_bp.route('/api/Listindicadores', methods=['GET'])
def api_lista_indicadores():
    indicadores = Indicador.query.all()
    return jsonify([
        {
            "id": ind.indicadorid,
            "institutionid": ind.institutionid,
            "grupoid": ind.grupoid,
            "descripcion": ind.descripcion,
            "numerador": ind.numerador,
            "numeradorctas": ind.numeradorctas,
            "denominador": ind.denominador,
            "denominadorctas": ind.denominadorctas
        }
        for ind in indicadores
    ])
@indicadores_bp.route('/api/Updateindicadores', methods=['POST'])
def editar_indicador_json():
    data = request.get_json()

    if not data or "id" not in data:
        return jsonify({"error": "Se requiere el campo 'id' en el JSON"}), 400

    indicador = Indicador.query.get(data["id"])
    if not indicador:
        return jsonify({"error": f"Indicador con id {data['id']} no existe"}), 404

    # Actualizar solo si vienen en el JSON
    if "institutionid" in data:
        indicador.institutionid = data["institutionid"]
    if "grupoid" in data:
        indicador.grupoid = data["grupoid"]
    if "descripcion" in data:
        indicador.descripcion = data["descripcion"]
    if "numerador" in data:
        indicador.numerador = data["numerador"]
    if "numeradorctas" in data:
        indicador.numeradorctas = data["numeradorctas"]
    if "denominador" in data:
        indicador.denominador = data["denominador"]
    if "denominadorctas" in data:
        indicador.denominadorctas = data["denominadorctas"]

    db.session.commit()

    return jsonify({
        "message": "Indicador actualizado correctamente",
        "indicador": {
            "id": indicador.indicadorid,
            "institutionid": indicador.institutionid,
            "grupoid": indicador.grupoid,
            "descripcion": indicador.descripcion,
            "numerador": indicador.numerador,
            "numeradorctas": indicador.numeradorctas,
            "denominador": indicador.denominador,
            "denominadorctas": indicador.denominadorctas
        }
    }), 200
@indicadores_bp.route('/api/Deleteindicadores', methods=['POST'])
def eliminar_indicador_json():
    data = request.get_json()

    if not data or "id" not in data:
        return jsonify({"error": "Se requiere el campo 'id' en el JSON"}), 400

    indicador = Indicador.query.get(data["id"])
    if not indicador:
        return jsonify({"error": f"Indicador con id {data['id']} no existe"}), 404

    db.session.delete(indicador)
    db.session.commit()

    return jsonify({
        "message": f"Indicador con id {data['id']} eliminado correctamente"
    }), 200
def validar_cuentas(cuentas_text):
    cuentas = [c.strip() for c in cuentas_text.split('+') if c.strip()]
    print(cuentas)
    faltantes = []
    
    for cuenta in cuentas:
        existe = TemplateBalance.query.filter_by(codigo=cuenta).first()
        
        if not existe:
            faltantes.append(cuenta)
    
    if faltantes:
        return False, f"No existen las cuentas: {', '.join(faltantes)}"
    return True, "OK"
@indicadores_bp.route('/api/Validarindicador', methods=['POST'])
def validar_indicador():
    data = request.get_json()

    numeradorctas = data.get('numerador', '')
    denominadorctas = data.get('denominador', '')

    # Validar numerador
    valido_num, msg_num = validar_cuentas(numeradorctas)
    if not valido_num:
        return jsonify({"status": "error", "message": msg_num}), 400

    # Validar denominador
    valido_den, msg_den = validar_cuentas(denominadorctas)
    if not valido_den:
        return jsonify({"status": "error", "message": msg_den}), 400

    return jsonify({"status": "success", "message": "Todas las cuentas existen."}), 200