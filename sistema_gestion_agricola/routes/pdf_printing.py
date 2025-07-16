# routes/pdf_printing.py
import os
import platform
from flask import Blueprint, render_template, make_response
import pdfkit
from ..models import db
from sqlalchemy.sql import text

pdf_bp = Blueprint('pdf', __name__, url_prefix='/pdf')

def get_wkhtmltopdf_path():
    path_env = os.getenv("WKHTMLTOPDF_BIN")
    if path_env and os.path.isfile(path_env):
        return path_env

    system = platform.system()
    if system == "Windows":
        path = os.path.join(os.getcwd(), "bin", "wkhtmltopdf.exe")
    elif system == "Linux":
        path = os.path.join(os.getcwd(), "bin", "wkhtmltopdf")
    else:
        raise RuntimeError(f"Sistema operativo no soportado: {system}")

    if not os.path.isfile(path):
        raise FileNotFoundError(f"wkhtmltopdf no encontrado en {path}")
    
    return path


@pdf_bp.route('/resumen_cuentas/pdf')
def exportar_resumen_pdf():
    resumen = db.session.execute(text('''
        SELECT p."ID", p."Nombre",
            COALESCE(SUM(c."Cantidad" * c."Precio_Unitario"), 0) AS "Total_Compras",
            COALESCE(SUM(pg."Monto"), 0) AS "Total_Pagos",
            (COALESCE(SUM(c."Cantidad" * c."Precio_Unitario"), 0) - COALESCE(SUM(pg."Monto"), 0)) AS "Saldo"
        FROM proveedores p
        LEFT JOIN compras c ON p."ID" = c."ID_Proveedor"
        LEFT JOIN pagos_proveedores pg ON p."ID" = pg."ID_Proveedor"
        GROUP BY p."ID", p."Nombre"
    ''')).fetchall()

    rendered = render_template('pagos/resumen_pdf.html', resumen=resumen)

    try:
        wkhtmltopdf_path = get_wkhtmltopdf_path()
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        pdf = pdfkit.from_string(rendered, False, configuration=config)
    except OSError:
        pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=resumen_cuentas.pdf'
    return response
