# routes/compras.py
from flask import Blueprint, request, render_template, redirect, url_for, flash
from ..models import db, Compra, Componente, Proveedor, Stock

compras_bp = Blueprint('compras', __name__, url_prefix='/compras')

# Historial de compras
@compras_bp.route('/')
def historial_compras():
    compras = (
        db.session.query(Compra)
        .join(Componente, Compra.ID_Componente == Componente.ID)
        .join(Proveedor, Compra.ID_Proveedor == Proveedor.ID)
        .order_by(Compra.Fecha.desc())
        .all()
    )
    return render_template('compras/historial.html', compras=compras)

# Vista detallada de una compra
@compras_bp.route('/<int:id_compra>')
def ver_compra(id_compra):
    compra = (
        db.session.query(Compra)
        .filter(Compra.ID_Compra == id_compra)
        .first()
    )
    if not compra:
        return render_template('404.html', message='Compra no encontrada'), 404
    return render_template('compras/ver.html', compra=compra)

# Registrar una nueva compra
@compras_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_compra():
    proveedores = Proveedor.query.all()
    componentes = Componente.query.all()

    if request.method == 'POST':
        proveedor_id = request.form.get('proveedor')
        componente_id = request.form.get('componente')
        cantidad = request.form.get('cantidad')
        precio_unitario = request.form.get('precio_unitario')
        observacion = request.form.get('observacion', '').strip()

        # Validaciones básicas
        if not proveedor_id or not componente_id or not cantidad or not precio_unitario:
            flash('Todos los campos obligatorios deben completarse.')
            return redirect(url_for('compras.registrar_compra'))

        try:
            cantidad_val = float(cantidad)
            precio_val = float(precio_unitario)
        except ValueError:
            flash('Cantidad y precio deben ser números válidos.')
            return redirect(url_for('compras.registrar_compra'))

        nueva_compra = Compra(
            ID_Proveedor=proveedor_id,
            ID_Componente=componente_id,
            Cantidad=cantidad_val,
            Precio_Unitario=precio_val,
            Observacion=observacion
        )
        db.session.add(nueva_compra)
        db.session.flush()  # Para obtener ID si necesitás

        # Agregar stock
        entrada_stock = Stock(
            ID_Componente=componente_id,
            Cantidad=cantidad_val,
            Tipo='entrada',
            Observacion=f'Compra de proveedor ID {proveedor_id}: {observacion or "sin observación"}'
        )
        db.session.add(entrada_stock)
        db.session.commit()

        flash('Compra registrada correctamente.')
        return redirect(url_for('stock.vista_stock'))

    return render_template(
        'compras/registrar.html',
        proveedores=proveedores,
        componentes=componentes
    )

# Editar una compra existente
@compras_bp.route('/editar/<int:id_compra>', methods=['GET', 'POST'])
def editar_compra(id_compra):
    compra = Compra.query.get(id_compra)
    if not compra:
        return render_template('404.html', message='Compra no encontrada'), 404

    proveedores = Proveedor.query.all()
    componentes = Componente.query.all()

    if request.method == 'POST':
        proveedor_id = request.form.get('proveedor')
        componente_id = request.form.get('componente')
        cantidad = request.form.get('cantidad')
        precio_unitario = request.form.get('precio_unitario')
        observacion = request.form.get('observacion', '').strip()

        if not proveedor_id or not componente_id or not cantidad or not precio_unitario:
            flash('Todos los campos obligatorios deben completarse.')
            return redirect(url_for('compras.editar_compra', id_compra=id_compra))

        try:
            cantidad_val = float(cantidad)
            precio_val = float(precio_unitario)
        except ValueError:
            flash('Cantidad y precio deben ser números válidos.')
            return redirect(url_for('compras.editar_compra', id_compra=id_compra))

        compra.ID_Proveedor = proveedor_id
        compra.ID_Componente = componente_id
        compra.Cantidad = cantidad_val
        compra.Precio_Unitario = precio_val
        compra.Observacion = observacion

        db.session.commit()
        flash('Compra actualizada correctamente.')
        return redirect(url_for('compras.ver_compra', id_compra=id_compra))

    return render_template('compras/editar.html',
                           compra=compra,
                           proveedores=proveedores,
                           componentes=componentes)
