from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
import io
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import text
from app.models import Grupo, Indicador, Pais, TempInd, Template_Balance

indicador_bp = Blueprint('indicador_bp', __name__)

# Crear indicador
@indicador_bp.route('/api/indicador/create', methods=['POST'])
def crear_indicador():
    data = request.get_json()

    grupoid = data.get('grupoid')
    clavepais = data.get('clavepais')
    indicador_nombre = data.get('indicador')
    descripcion = data.get('descripcion')
    formula = data.get('formula')  # Espera JSON
    templateid = data.get('templateid')

    if not grupoid or not indicador_nombre:
        return jsonify({"error": "grupoid e indicador son requeridos"}), 400

    # Validar existencia de grupo
    if not Grupo.query.get(grupoid):
        return jsonify({"error": "Grupo no existe"}), 404

    # Validar clavepais opcional
    if clavepais and not Pais.query.get(clavepais):
        return jsonify({"error": "País no existe"}), 404

    # Si se pasa templateid, validar que exista el template
    if templateid:
        template = Template_Balance.query.get(templateid)
        if not template:
            return jsonify({"error": "Template no existe"}), 404
        universo = False
    else:
        universo = True

    # Validar si ya existe el indicador
    indicador_existente = Indicador.query.filter_by(
        grupoid=grupoid,
        clavepais=clavepais,
        indicador=indicador_nombre
    ).first()

    if indicador_existente:
        return jsonify({"error": "El indicador ya existe para este grupo y país"}), 409

    # Crear nuevo indicador
    indicador = Indicador(
        grupoid=grupoid,
        clavepais=clavepais,
        indicador=indicador_nombre,
        descripcion=descripcion,
        formula=formula if not templateid else None,  # si tiene template, se guarda en TempInd
        universo=universo
    )
    db.session.add(indicador)
    db.session.commit()

    # Si se pasó templateid, crear la relación en TempInd
    if templateid:
        temp_ind = TempInd(
            indicadorid=indicador.indicadorid,
            templateid=templateid,
            formula=formula  # Guardamos la fórmula en la tabla TempInd
        )
        db.session.add(temp_ind)
        db.session.commit()

    return jsonify({
        "message": "Indicador creado exitosamente",
        "indicadorid": indicador.indicadorid,
        "grupoid": indicador.grupoid,
        "clavepais": indicador.clavepais,
        "indicador": indicador.indicador,
        "universo": indicador.universo,
        "templateid": templateid if templateid else None
    }), 201
# Listar indicadores
@indicador_bp.route('/api/indicador/list', methods=['POST'])
def listar_indicadores():
    data = request.json or {}
    indicadorid = data.get('indicadorid')
    clavepais = data.get('clavepais')
    templateid = data.get('templateid')  # <-- Nuevo parámetro

    # Si se envía un ID específico
    if indicadorid:
        indicador = Indicador.query.get(indicadorid)
        if not indicador:
            return jsonify({"error": f"No se encontró el indicador con id {indicadorid}"}), 404
        
        result = {
            "indicadorid": indicador.indicadorid,
            "grupoid": indicador.grupoid,
            "clavepais": indicador.clavepais,
            "indicador": indicador.indicador,
            "descripcion": indicador.descripcion,
            "formula": indicador.formula
        }
        return jsonify(result), 200

    # Si se envía un templateid, listamos solo los indicadores asociados
    elif templateid:
        indicadores = (
            db.session.query(Indicador, TempInd)
            .join(TempInd, TempInd.indicadorid == Indicador.indicadorid)
            .filter(TempInd.templateid == templateid)
            .all()
        )

        if not indicadores:
            return jsonify({"message": f"No se encontraron indicadores para el templateid '{templateid}'"}), 404
        
        # Construimos el resultado usando la fórmula de TempInd si no es nula
        result = [
            {
                "indicadorid": ind.indicadorid,
                "grupoid": ind.grupoid,
                "clavepais": ind.clavepais,
                "indicador": ind.indicador,
                "descripcion": ind.descripcion,
                "formula": temp.formula if temp.formula else ind.formula
            }
            for ind, temp in indicadores
        ]

    # Si se envía clavepais
    elif clavepais:
        indicadores = Indicador.query.filter_by(clavepais=clavepais, universo=True).all()
        if not indicadores:
            return jsonify({"message": f"No se encontraron indicadores para clavepais '{clavepais}'"}), 404
        # Construimos el resultado
        result = [
            {
                "indicadorid": i.indicadorid,
                "grupoid": i.grupoid,
                "clavepais": i.clavepais,
                "indicador": i.indicador,
                "descripcion": i.descripcion,
                "formula": i.formula
            } for i in indicadores
        ]

    # Si no hay filtros, retorna todos
    else:
        indicadores = Indicador.query.all()

        # Construimos el resultado
        result = [
            {
                "indicadorid": i.indicadorid,
                "grupoid": i.grupoid,
                "clavepais": i.clavepais,
                "indicador": i.indicador,
                "descripcion": i.descripcion,
                "formula": i.formula
            } for i in indicadores
        ]

    return jsonify(result), 200
# Servicio para modificar la fórmula del indicador
@indicador_bp.route('/api/indicador/update_formula', methods=['POST'])
def actualizar_formula_indicador():
    data = request.get_json()

    indicadorid = data.get('indicadorid')
    formula = data.get('formula')

    if not indicadorid or not formula:
        return jsonify({"error": "indicadorid y formula son requeridos"}), 400

    indicador = Indicador.query.get(indicadorid)
    if not indicador:
        return jsonify({"error": f"No se encontró el indicador con id {indicadorid}"}), 404

    # Actualizar fórmula
    indicador.formula = formula
    db.session.commit()

    return jsonify({
        "message": "Fórmula del indicador actualizada exitosamente",
        "indicadorid": indicador.indicadorid,
        "formula": indicador.formula
    }), 200
# Servicio para modificar la fórmula de un indicador asociado a un template
@indicador_bp.route('/api/tempind/update_formula', methods=['POST'])
def actualizar_formula_tempind():
    data = request.get_json()

    indicadorid = data.get('indicadorid')
    templateid = data.get('templateid')
    formula = data.get('formula')

    if not indicadorid or not templateid or not formula:
        return jsonify({"error": "indicadorid, templateid y formula son requeridos"}), 400

    tempind = TempInd.query.filter_by(indicadorid=indicadorid, templateid=templateid).first()
    if not tempind:
        return jsonify({"error": f"No existe relación entre templateid {templateid} e indicadorid {indicadorid}"}), 404

    # Actualizar fórmula del template
    tempind.formula = formula
    db.session.commit()

    return jsonify({
        "message": "Fórmula del indicador-template actualizada exitosamente",
        "templateid": tempind.templateid,
        "indicadorid": tempind.indicadorid,
        "formula": tempind.formula
    }), 200