from ..models import db, Componente, Stock
from sqlalchemy import func, case

def obtener_stock_actual():
    saldo = func.coalesce(
        func.sum(
            case(
                (Stock.Tipo == 'entrada', Stock.Cantidad),
                (Stock.Tipo == 'salida', -Stock.Cantidad),
                else_=0
            )
        ),
        0
    ).label('Stock_Actual')

    resultados = (
        db.session.query(
            Componente.ID.label("ID"),
            Componente.ID_Componente.label("ID_Componente"),
            Componente.Nombre.label("Nombre"),
            Componente.Tipo.label("Tipo"),
            Componente.Descripcion.label("Descripcion"),
            Componente.Foto.label("Foto"),
            saldo
        )
        .outerjoin(Stock, Componente.ID == Stock.ID_Componente)
        .group_by(Componente.ID)
        .order_by(Componente.Nombre)
        .all()
    )

    # Convertir a dict-like
    return [dict(r._mapping) for r in resultados]
