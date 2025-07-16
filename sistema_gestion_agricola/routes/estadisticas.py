# routes/estadisticas.py
from flask import Blueprint, render_template
from ..models import Proveedor, Compra
from .. import db
from sqlalchemy import func

estadisticas_bp = Blueprint('estadisticas', __name__, url_prefix='/estadisticas')

@estadisticas_bp.route('/compras_proveedor')
def compras_por_proveedor():
    # Consulta con SQLAlchemy
    data = (
        db.session.query(
            Proveedor.Nombre,
            func.sum(Compra.Cantidad * Compra.Precio_Unitario).label('Total')
        )
        .join(Compra, Compra.ID_Proveedor == Proveedor.ID)
        .group_by(Proveedor.ID)
        .order_by(func.sum(Compra.Cantidad * Compra.Precio_Unitario).desc())
        .all()
    )

    labels = [row.Nombre for row in data]
    values = [row.Total for row in data]

    return render_template('estadisticas/compras_proveedor.html', labels=labels, values=values)
