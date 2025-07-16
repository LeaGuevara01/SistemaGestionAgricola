# routes/pagos.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import db, Proveedor, PagoProveedor
from sqlalchemy import func

pagos_bp = Blueprint('pagos', __name__, url_prefix='/pagos')

# Registrar pago a proveedor
@pagos_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_pago():
    proveedores = Proveedor.query.with_entities(Proveedor.ID, Proveedor.Nombre).all()

    if request.method == 'POST':
        id_proveedor = request.form.get('proveedor')
        monto = request.form.get('monto')
        metodo = request.form.get('metodo', '').strip()
        observacion = request.form.get('observacion', '').strip()

        # Validaciones básicas
        if not id_proveedor or not monto:
            flash('Proveedor y monto son obligatorios.')
            return redirect(url_for('pagos.registrar_pago'))

        try:
            monto_val = float(monto)
            if monto_val <= 0:
                raise ValueError
        except ValueError:
            flash('Monto inválido.')
            return redirect(url_for('pagos.registrar_pago'))

        pago = PagoProveedor(
            ID_Proveedor=id_proveedor,
            Monto=monto_val,
            Metodo=metodo,
            Observacion=observacion
        )

        db.session.add(pago)
        db.session.commit()

        flash('Pago registrado correctamente.')
        return redirect(url_for('pagos.resumen_cuentas'))

    return render_template('pagos/registrar.html', proveedores=proveedores)


# Resumen de cuentas por proveedor
@pagos_bp.route('/resumen')
def resumen_cuentas():
    # Subconsultas para total compras y total pagos por proveedor
    from ..models import Compra

    total_compras_subq = db.session.query(
        Compra.ID_Proveedor,
        func.coalesce(func.sum(Compra.Cantidad * Compra.Precio_Unitario), 0).label('total_compras')
    ).group_by(Compra.ID_Proveedor).subquery()

    total_pagos_subq = db.session.query(
        PagoProveedor.ID_Proveedor,
        func.coalesce(func.sum(PagoProveedor.Monto), 0).label('total_pagos')
    ).group_by(PagoProveedor.ID_Proveedor).subquery()

    resumen = db.session.query(
        Proveedor.ID,
        Proveedor.Nombre,
        func.coalesce(total_compras_subq.c.total_compras, 0).label('Total_Compras'),
        func.coalesce(total_pagos_subq.c.total_pagos, 0).label('Total_Pagos'),
        (func.coalesce(total_compras_subq.c.total_compras, 0) - func.coalesce(total_pagos_subq.c.total_pagos, 0)).label('Saldo')
    ).outerjoin(
        total_compras_subq, Proveedor.ID == total_compras_subq.c.ID_Proveedor
    ).outerjoin(
        total_pagos_subq, Proveedor.ID == total_pagos_subq.c.ID_Proveedor
    ).order_by(Proveedor.Nombre).all()

    return render_template('pagos/resumen.html', resumen=resumen)


# Listar pagos de un proveedor específico
@pagos_bp.route('/proveedor/<int:id_proveedor>')
def listar_pagos(id_proveedor):
    proveedor = Proveedor.query.get(id_proveedor)
    if not proveedor:
        flash('Proveedor no encontrado.')
        return redirect(url_for('pagos.resumen_cuentas'))

    pagos = PagoProveedor.query.filter_by(ID_Proveedor=id_proveedor).order_by(PagoProveedor.Fecha.desc()).all()

    return render_template('pagos/listar.html', pagos=pagos, proveedor=proveedor)
