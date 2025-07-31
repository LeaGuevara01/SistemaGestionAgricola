from ..models.maquina import Maquina
from ..utils.db import db

def bulk_import_machines(data):
    """Importa máquinas de forma masiva"""
    imported = []
    errors = []
    
    for index, row in enumerate(data):
        try:
            # Verificar si ya existe por número de serie
            if row.get('numero_serie'):
                existing = Maquina.query.filter_by(numero_serie=row['numero_serie']).first()
                if existing:
                    errors.append(f"Fila {index + 2}: Máquina con número de serie '{row['numero_serie']}' ya existe")
                    continue
            
            # Convertir valores
            año = None
            if row.get('año') and str(row['año']).strip():
                try:
                    año = int(row['año'])
                except ValueError:
                    errors.append(f"Fila {index + 2}: Año inválido '{row['año']}'")
                    continue
            
            horas_trabajo = 0
            if row.get('horas_trabajo') and str(row['horas_trabajo']).strip():
                try:
                    horas_trabajo = float(row['horas_trabajo'])
                except ValueError:
                    horas_trabajo = 0
            
            activo = True
            if row.get('activo'):
                activo_str = str(row['activo']).lower().strip()
                activo = activo_str in ['true', '1', 'si', 'yes', 'verdadero']
            
            maquina = Maquina(
                nombre=row['nombre'],
                marca=row.get('marca', ''),
                modelo=row.get('modelo', ''),
                numero_serie=row.get('numero_serie'),
                año=año,
                tipo=row.get('tipo', ''),
                estado=row.get('estado', 'operativo'),
                horas_trabajo=horas_trabajo,
                ubicacion=row.get('ubicacion', ''),
                observaciones=row.get('observaciones', ''),
                activo=activo
            )
            
            db.session.add(maquina)
            imported.append(maquina.to_dict())
            
        except Exception as e:
            errors.append(f"Fila {index + 2}: {str(e)}")
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {'imported': [], 'errors': [f"Error al guardar en base de datos: {str(e)}"]}
    
    return {'imported': imported, 'errors': errors}