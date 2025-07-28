from flask import request, jsonify
from app.services.file_service import FileService
from app.services.csv_parser import parse_csv
from app.services.data_validator import validate_machine_data
from app.services.bulk_import_service import bulk_import_machines

def import_machines_from_csv():
    """Importar máquinas desde CSV"""
    try:
        if 'csvFile' not in request.files:
            return jsonify({'error': 'No se proporcionó archivo CSV'}), 400
        
        file = request.files['csvFile']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        try:
            filepath = FileService.save_import_file(file, 'imports/maquinas')
            if not filepath:
                return jsonify({'error': 'Tipo de archivo no permitido. Solo CSV, XLS, XLSX'}), 400
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Validar estructura del CSV
        required_columns = ['nombre', 'marca', 'modelo']
        structure_validation = FileService.validate_csv_structure(filepath, required_columns)
        
        if not structure_validation['valid']:
            FileService.cleanup_temp_file(filepath)
            return jsonify({
                'error': 'Estructura de CSV inválida',
                'details': structure_validation['error']
            }), 400
        
        # Parsear CSV
        csv_data = parse_csv(filepath)
        
        # Validar datos
        validation_result = validate_machine_data(csv_data)
        if not validation_result['is_valid']:
            FileService.cleanup_temp_file(filepath)
            return jsonify({
                'error': 'Datos inválidos',
                'details': validation_result['errors']
            }), 400
        
        # Importar datos
        result = bulk_import_machines(csv_data)
        
        # Limpiar archivo temporal
        FileService.cleanup_temp_file(filepath)
        
        return jsonify({
            'success': True,
            'imported': result['imported'],
            'errors': result['errors'],
            'total': len(csv_data)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error en la importación: {str(e)}'}), 500

def get_import_template():
    """Generar plantilla CSV para máquinas"""
    try:
        template_data = {
            'nombre': ['Tractor John Deere', 'Cosechadora Case'],
            'marca': ['John Deere', 'Case IH'],
            'modelo': ['6110M', 'Axial Flow 2388'],
            'numero_serie': ['JD123456', 'CASE789012'],
            'año': ['2020', '2018'],
            'tipo': ['tractor', 'cosechadora'],
            'estado': ['operativo', 'operativo'],
            'horas_trabajo': ['1500', '2800'],
            'ubicacion': ['Campo Norte', 'Galpón Principal'],
            'observaciones': ['Tractor principal', 'Necesita revisión'],
            'activo': ['True', 'True']
        }
        
        import pandas as pd
        from flask import make_response
        import io
        
        df = pd.DataFrame(template_data)
        
        # Crear CSV en memoria
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=maquinas_template.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Error generando plantilla: {str(e)}'}), 500