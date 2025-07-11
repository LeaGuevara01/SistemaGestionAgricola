# routes/stock.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..utils.db import get_db_connection
from datetime import datetime

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')

# List Stock
@stock_bp.route('/')
def vista_stock():
    conn = get_db_connection()
    # This query needs to be updated to use the stock_utils function
    from ..utils.stock_utils import obtener_stock_actual
    stock = obtener_stock_actual()
    conn.close()
    return render_template('stock/listar.html', stock=stock)

# Register Stock Movement
@stock_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_stock():
    conn = get_db_connection()
    componentes = conn.execute('SELECT ID_Componente, Nombre FROM componentes').fetchall()

    if request.method == 'POST':
        id_componente = request.form['id_componente']
        cantidad = int(request.form['cantidad'])
        tipo = request.form['tipo']
        observacion = request.form['observacion']

        conn.execute('''
            INSERT INTO stock (ID_Componente, Cantidad, Tipo, Observacion)
            VALUES (?, ?, ?, ?)
        ''', (id_componente, cantidad, tipo, observacion))
        conn.commit()
        conn.close()
        return redirect(url_for('stock.vista_stock'))

    conn.close()
    return render_template('stock/registrar.html', componentes=componentes)


# Read Stock Detail
@stock_bp.route('/<int:id>')
def detalle_stock(id):
    conn = get_db_connection()
    componente = conn.execute('SELECT * FROM componentes WHERE ID = ?', (id,)).fetchone()
    movimientos = conn.execute('''
        SELECT * FROM stock
        WHERE ID_Componente = ?
        ORDER BY Fecha DESC
    ''', (id,)).fetchall()
    conn.close()

    if not componente:
        flash("Componente no encontrado.")
        return redirect(url_for('stock.vista_stock'))

    return render_template('stock/detalle.html', componente=componente, movimientos=movimientos)
