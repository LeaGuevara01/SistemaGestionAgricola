# routes/stock.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import db, Componente, Stock
from datetime import datetime

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')

# Listar stock actual usando función utilitaria (que deberá usar SQLAlchemy)
@stock_bp.route('/')
def vista_stock():
    from ..utils.stock_utils import obtener_stock_actual
    stock = obtener_stock_actual()
    return render_template('stock/listar.html', stock=stock)

# Registrar movimiento de stock
@stock_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_stock():
    componentes = Componente.query.all()

    if request.method == 'POST':
        id_componente = request.form.get('id_componente')
        cantidad = request.form.get('cantidad')
        tipo = request.form.get('tipo')
        observacion = request.form.get('observacion', '').strip()

        if not id_componente or not cantidad or not tipo:
            flash('Completar todos los campos obligatorios.')
            return redirect(url_for('stock.registrar_stock'))

        try:
            cantidad_val = int(cantidad)
        except ValueError:
            flash('Cantidad debe ser un número entero válido.')
            return redirect(url_for('stock.registrar_stock'))

        nuevo_movimiento = Stock(
            ID_Componente=id_componente,
            Cantidad=cantidad_val,
            Tipo=tipo,
            Observacion=observacion,
            Fecha=datetime.utcnow()
        )

        db.session.add(nuevo_movimiento)
        db.session.commit()

        flash('Movimiento de stock registrado correctamente.')
        return redirect(url_for('stock.vista_stock'))

    return render_template('stock/registrar.html', componentes=componentes)

# Detalle del stock y movimientos asociados a un componente
@stock_bp.route('/<int:id>')
def detalle_stock(id):
    componente = Componente.query.get(id)
    if not componente:
        flash('Componente no encontrado.')
        return redirect(url_for('stock.vista_stock'))

    movimientos = Stock.query.filter_by(ID_Componente=id).order_by(Stock.Fecha.desc()).all()

    return render_template('stock/detalle.html', componente=componente, movimientos=movimientos)
