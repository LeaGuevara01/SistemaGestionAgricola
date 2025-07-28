from flask import Blueprint
from app.controllers.import_controller import (
    import_machines_from_csv, 
    import_components_from_csv,
    get_import_template
)

import_bp = Blueprint('import', __name__, url_prefix='/import')

@import_bp.route('/machines', methods=['POST'])
def import_machines():
    """Importar máquinas desde CSV"""
    return import_machines_from_csv()

@import_bp.route('/components', methods=['POST'])
def import_components():
    """Importar componentes desde CSV"""
    return import_components_from_csv()

@import_bp.route('/templates/<template_type>', methods=['GET'])
def download_template(template_type):
    """Descargar plantillas CSV"""
    return get_import_template(template_type)

@import_bp.route('/validate/<template_type>', methods=['POST'])
def validate_csv():
    """Validar CSV sin importar"""
    from app.controllers.import_controller import validate_csv_file
    return validate_csv_file()