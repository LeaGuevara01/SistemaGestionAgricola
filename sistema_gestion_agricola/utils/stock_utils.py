from .db import get_db_connection

def obtener_stock_actual():
    conn = get_db_connection()
    stock_query = '''
        SELECT 
            c.ID,
            c.ID_Componente,
            c.Nombre,
            c.Tipo,
            c.Descripcion,
            c.Foto,
            COALESCE(SUM(
                CASE s.Tipo
                    WHEN 'entrada' THEN s.Cantidad
                    WHEN 'salida' THEN -s.Cantidad
                END
            ), 0) AS Stock_Actual
        FROM componentes c
        LEFT JOIN stock s ON c.ID = s.ID_Componente
        GROUP BY c.ID
        ORDER BY c.Nombre
    '''
    res = conn.execute(stock_query).fetchall()
    conn.close()
    return res
