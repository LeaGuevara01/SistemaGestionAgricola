# routes/pagos.py
from flask import Blueprint, render_template, request, redirect, url_for
from ..utils.db import get_db_connection

pagos_bp = Blueprint('pagos', __name__, url_prefix='/pagos')

# Payment to Providers
@pagos_bp.route('/registrar', methods=['GET', 'POST'])
def registrar_pago():
    conn = get_db_connection()
    proveedores = conn.execute('SELECT ID, Nombre FROM proveedores').fetchall()

    if request.method == 'POST':
        id_proveedor = request.form['proveedor']
        monto = float(request.form['monto'])
        metodo = request.form['metodo']
        observacion = request.form['observacion']

        conn.execute('''
            INSERT INTO pagos_proveedores (ID_Proveedor, Monto, Metodo, Observacion)
            VALUES (?, ?, ?, ?)
        ''', (id_proveedor, monto, metodo, observacion))

        conn.commit()
        conn.close()
        return redirect(url_for('pagos.resumen_cuentas'))

    conn.close()
    return render_template('pagos/registrar.html', proveedores=proveedores)

# Summary of Accounts
@pagos_bp.route('/resumen')
def resumen_cuentas():
    conn = get_db_connection()
    resumen = conn.execute('''
        SELECT 
            p.ID, p.Nombre,
        IFNULL((SELECT SUM(c.Cantidad * c.Precio_Unitario) 
                    FROM compras c 
                    WHERE c.ID_Proveedor = p.ID), 0) AS Total_Compras,
        IFNULL((SELECT SUM(pg.Monto) 
                    FROM pagos_proveedores pg 
                    WHERE pg.ID_Proveedor = p.ID), 0) AS Total_Pagos,
        (IFNULL((SELECT SUM(c.Cantidad * c.Precio_Unitario) 
                    FROM compras c 
                    WHERE c.ID_Proveedor = p.ID), 0) - 
        IFNULL((SELECT SUM(pg.Monto) 
                    FROM pagos_proveedores pg 
                    WHERE pg.ID_Proveedor = p.ID), 0)
        ) AS Saldo
    FROM proveedores p
    ORDER BY p.Nombre;
    ''').fetchall()
    conn.close()
    return render_template('pagos/resumen.html', resumen=resumen)
