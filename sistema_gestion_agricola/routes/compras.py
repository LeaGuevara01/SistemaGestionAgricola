# routes/compras.py
from flask import Blueprint, request, render_template, redirect, url_for
from ..utils.db import get_db_connection

compras_bp = Blueprint('compras', __name__, url_prefix='/compras')

# Purchase History
@compras_bp.route('/')
def historial_compras():
    conn = get_db_connection()
    compras = conn.execute('''
        SELECT co.Fecha, co.ID_Compra, co.Cantidad, co.Precio_Unitario, co.Observacion,
               c.Nombre AS Nombre_Componente,
               p.Nombre AS Nombre_Proveedor
        FROM compras co
        JOIN componentes c ON co.ID_Componente = c.ID
        JOIN proveedores p ON co.ID_Proveedor = p.ID
        ORDER BY co.Fecha DESC
    ''').fetchall()
    conn.close()
    return render_template('compras/historial.html', compras=compras)

# Purchase View
@compras_bp.route('/<int:id_compra>')
def ver_compra(id_compra):
    conn = get_db_connection()

    compra = conn.execute('''
        SELECT 
            c.ID_Compra,
            c.Cantidad,
            c.Precio_Unitario,
            c.Fecha,
            c.Observacion,
            p.ID AS ID_Proveedor,
            p.Nombre AS Nombre_Proveedor,
            comp.ID AS ID_Componente,
            comp.Nombre AS Nombre_Componente,
            comp.Tipo,
            comp.Foto
        FROM compras c
        LEFT JOIN proveedores p ON c.ID_Proveedor = p.ID
        LEFT JOIN componentes comp ON c.ID_Componente = comp.ID
        WHERE c.ID_Compra = ?
    ''', (id_compra,)).fetchone()

    conn.close()

    if compra is None:
        return render_template('404.html', message='Compra no encontrada'), 404

    return render_template('compras/ver.html', compra=compra)

# Purchase Registration
@compras_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_compra():
    conn = get_db_connection()
    proveedores = conn.execute('SELECT ID, Nombre FROM proveedores').fetchall()
    componentes = conn.execute('SELECT ID, Nombre FROM componentes').fetchall()

    if request.method == 'POST':
        proveedor_id = request.form['proveedor']
        componente_id = request.form['componente']
        cantidad = request.form['cantidad']
        precio_unitario = request.form['precio_unitario']
        observacion = request.form.get('observacion', '').strip()

        # Insert purchase into 'compras' table
        conn.execute('''
            INSERT INTO compras (ID_Proveedor, ID_Componente, Cantidad, Precio_Unitario, Observacion)
            VALUES (?, ?, ?, ?, ?)
        ''', (proveedor_id, componente_id, cantidad, precio_unitario, observacion))

        # Insert stock entry
        conn.execute('''
            INSERT INTO stock (ID_Componente, Cantidad, Tipo, Observacion)
            VALUES (?, ?, 'entrada', ?)
        ''', (
            componente_id,
            cantidad,
            f'Compra de proveedor ID {proveedor_id}: {observacion or "sin observación"}'
        ))

        conn.commit()
        conn.close()
        return redirect(url_for('stock.vista_stock'))

    conn.close()
    return render_template(
        'compras/registrar.html',
        proveedores=proveedores,
        componentes=componentes
    )

# Purchase Edit
@compras_bp.route('/editar/<int:id_compra>', methods=['GET', 'POST'])
def editar_compra(id_compra):
    conn = get_db_connection()

    # Obtener la compra actual
    compra = conn.execute('''
        SELECT * FROM compras WHERE ID_Compra = ?
    ''', (id_compra,)).fetchone()

    if compra is None:
        conn.close()
        return render_template('404.html', message='Compra no encontrada'), 404

    # Obtener datos auxiliares
    proveedores = conn.execute('SELECT ID, Nombre FROM proveedores').fetchall()
    componentes = conn.execute('SELECT ID, Nombre FROM componentes').fetchall()

    if request.method == 'POST':
        proveedor_id = request.form['proveedor']
        componente_id = request.form['componente']
        cantidad = request.form['cantidad']
        precio_unitario = request.form['precio_unitario']
        observacion = request.form.get('observacion', '').strip()

        # Actualizar compra
        conn.execute('''
            UPDATE compras
            SET ID_Proveedor = ?, ID_Componente = ?, Cantidad = ?, Precio_Unitario = ?, Observacion = ?
            WHERE ID_Compra = ?
        ''', (proveedor_id, componente_id, cantidad, precio_unitario, observacion, id_compra))

        conn.commit()
        conn.close()
        return redirect(url_for('compras.ver_compra', id_compra=id_compra))

    conn.close()
    return render_template('compras/editar.html',
                           compra=compra,
                           proveedores=proveedores,
                           componentes=componentes)

