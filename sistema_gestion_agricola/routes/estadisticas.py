from flask import Blueprint, render_template
from ..utils.db import get_db_connection

estadisticas_bp = Blueprint('estadisticas', __name__, url_prefix='/estadisticas')

# Purchases by Provider
@estadisticas_bp.route('/compras_proveedor')
def compras_por_proveedor():
    conn = get_db_connection()
    data = conn.execute('''
        SELECT p.Nombre, SUM(c.Cantidad * c.Precio_Unitario) as Total
        FROM compras c
        JOIN proveedores p ON c.ID_Proveedor = p.ID
        GROUP BY p.ID
        ORDER BY Total DESC
    ''').fetchall()
    conn.close()

    labels = [row['Nombre'] for row in data]
    values = [row['Total'] for row in data]

    return render_template('estadisticas/compras_proveedor.html', labels=labels, values=values)
