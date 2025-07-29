import pandas as pd
import chardet
from flask import make_response
import io
from ..models import Maquina, Componente
from ..utils.db import db

class ImportService:
    
    @staticmethod
    def parse_csv(file_path):
        """Parsea un archivo CSV y retorna una lista de diccionarios"""
        try:
            # Detectar encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
            
            # Leer CSV con pandas
            df = pd.read_csv(file_path, encoding=encoding)
            
            # Limpiar datos
            df = df.fillna('')
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            
            return df.to_dict('records')
            
        except Exception as e:
            raise Exception(f"Error al parsear CSV: {str(e)}")
    
    @staticmethod
    def validate_maquinas_data(data):
        """Valida los datos de máquinas"""
        errors = []
        required_fields = ['nombre']
        
        for index, row in enumerate(data):
            # Validar campos requeridos
            for field in required_fields:
                if not row.get(field) or str(row[field]).strip() == '':
                    errors.append(f"Fila {index + 2}: Campo '{field}' es requerido")
            
            # Validar número de serie único si existe
            numero_serie = row.get('numero_serie')
            if numero_serie and str(numero_serie).strip():
                # Verificar duplicados en el mismo CSV
                duplicates = [i for i, other in enumerate(data) 
                             if i != index and other.get('numero_serie') == numero_serie]
                if duplicates:
                    errors.append(f"Fila {index + 2}: Número de serie '{numero_serie}' duplicado en el CSV")
                
                # Verificar si ya existe en la base de datos
                existing = Maquina.query.filter_by(numero_serie=numero_serie).first()
                if existing:
                    errors.append(f"Fila {index + 2}: Número de serie '{numero_serie}' ya existe en la base de datos")
            
            # Validar año si existe
            año = row.get('año')
            if año and str(año).strip():
                try:
                    año_int = int(año)
                    if año_int < 1900 or año_int > 2030:
                        errors.append(f"Fila {index + 2}: Año '{año}' fuera del rango válido (1900-2030)")
                except ValueError:
                    errors.append(f"Fila {index + 2}: Año '{año}' no es un número válido")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def import_maquinas_from_csv(file_path):
        """Importa máquinas desde CSV"""
        # Parsear CSV
        csv_data = ImportService.parse_csv(file_path)
        
        # Validar datos
        validation = ImportService.validate_maquinas_data(csv_data)
        if not validation['is_valid']:
            return {
                'imported': [],
                'errors': validation['errors'],
                'total': len(csv_data)
            }
        
        # Importar datos
        imported = []
        errors = []
        
        for index, row in enumerate(csv_data):
            try:
                # Convertir valores
                año = None
                if row.get('año') and str(row['año']).strip():
                    try:
                        año = int(row['año'])
                    except ValueError:
                        pass
                
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
                    numero_serie=row.get('numero_serie') if row.get('numero_serie') else None,
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
            return {
                'imported': [],
                'errors': [f"Error al guardar en base de datos: {str(e)}"],
                'total': len(csv_data)
            }
        
        return {
            'imported': imported,
            'errors': errors,
            'total': len(csv_data)
        }
    
    @staticmethod
    def get_maquinas_template():
        """Genera plantilla CSV para máquinas"""
        template_data = {
            'nombre': ['Tractor John Deere 6110M', 'Cosechadora Case Axial Flow'],
            'marca': ['John Deere', 'Case IH'],
            'modelo': ['6110M', 'Axial Flow 2388'],
            'numero_serie': ['JD123456', 'CASE789012'],
            'año': ['2020', '2018'],
            'tipo': ['tractor', 'cosechadora'],
            'estado': ['operativo', 'mantenimiento'],
            'horas_trabajo': ['1500', '2800'],
            'ubicacion': ['Campo Norte', 'Galpón Principal'],
            'observaciones': ['Tractor principal para labores', 'Necesita revisión general'],
            'activo': ['True', 'True']
        }
        
        df = pd.DataFrame(template_data)
        
        # Crear CSV en memoria
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=plantilla_maquinas.csv'
        
        return response
    
    @staticmethod
    def validate_componentes_data(data):
        """Valida los datos de componentes"""
        errors = []
        required_fields = ['nombre']
        
        for index, row in enumerate(data):
            # Validar campos requeridos
            for field in required_fields:
                if not row.get(field) or str(row[field]).strip() == '':
                    errors.append(f"Fila {index + 2}: Campo '{field}' es requerido")
            
            # Validar número de parte único si existe
            numero_parte = row.get('numero_parte')
            if numero_parte and str(numero_parte).strip():
                # Verificar duplicados en el mismo CSV
                duplicates = [i for i, other in enumerate(data) 
                             if i != index and other.get('numero_parte') == numero_parte]
                if duplicates:
                    errors.append(f"Fila {index + 2}: Número de parte '{numero_parte}' duplicado en el CSV")
                
                # Verificar si ya existe en la base de datos
                existing = Componente.query.filter_by(numero_parte=numero_parte).first()
                if existing:
                    errors.append(f"Fila {index + 2}: Número de parte '{numero_parte}' ya existe en la base de datos")
            
            # Validar precio unitario si existe
            precio = row.get('precio_unitario')
            if precio and str(precio).strip():
                try:
                    precio_float = float(precio)
                    if precio_float < 0:
                        errors.append(f"Fila {index + 2}: Precio unitario no puede ser negativo")
                except ValueError:
                    errors.append(f"Fila {index + 2}: Precio unitario '{precio}' no es un número válido")
            
            # Validar stock mínimo si existe
            stock_minimo = row.get('stock_minimo')
            if stock_minimo and str(stock_minimo).strip():
                try:
                    stock_int = int(stock_minimo)
                    if stock_int < 0:
                        errors.append(f"Fila {index + 2}: Stock mínimo no puede ser negativo")
                except ValueError:
                    errors.append(f"Fila {index + 2}: Stock mínimo '{stock_minimo}' no es un número válido")
            
            # Validar stock actual si existe
            stock_actual = row.get('stock_actual')
            if stock_actual and str(stock_actual).strip():
                try:
                    stock_int = int(stock_actual)
                    if stock_int < 0:
                        errors.append(f"Fila {index + 2}: Stock actual no puede ser negativo")
                except ValueError:
                    errors.append(f"Fila {index + 2}: Stock actual '{stock_actual}' no es un número válido")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def import_componentes_from_csv(file_path):
        """Importa componentes desde CSV"""
        # Parsear CSV
        csv_data = ImportService.parse_csv(file_path)
        
        # Validar datos
        validation = ImportService.validate_componentes_data(csv_data)
        if not validation['is_valid']:
            return {
                'imported': [],
                'errors': validation['errors'],
                'total': len(csv_data)
            }
        
        # Importar datos
        imported = []
        errors = []
        
        for index, row in enumerate(csv_data):
            try:
                # Convertir valores
                precio_unitario = 0
                if row.get('precio_unitario') and str(row['precio_unitario']).strip():
                    try:
                        precio_unitario = float(row['precio_unitario'])
                    except ValueError:
                        precio_unitario = 0
                
                stock_minimo = 0
                if row.get('stock_minimo') and str(row['stock_minimo']).strip():
                    try:
                        stock_minimo = int(row['stock_minimo'])
                    except ValueError:
                        stock_minimo = 0
                
                stock_actual = 0
                if row.get('stock_actual') and str(row['stock_actual']).strip():
                    try:
                        stock_actual = int(row['stock_actual'])
                    except ValueError:
                        stock_actual = 0
                
                activo = True
                if row.get('activo'):
                    activo_str = str(row['activo']).lower().strip()
                    activo = activo_str in ['true', '1', 'si', 'yes', 'verdadero']
                
                componente = Componente(
                    nombre=row['nombre'],
                    descripcion=row.get('descripcion', ''),
                    numero_parte=row.get('numero_parte') if row.get('numero_parte') else None,
                    categoria=row.get('categoria', ''),
                    precio_unitario=precio_unitario,
                    stock_minimo=stock_minimo,
                    stock_actual=stock_actual,
                    activo=activo
                )
                
                db.session.add(componente)
                imported.append(componente.to_dict())
                
            except Exception as e:
                errors.append(f"Fila {index + 2}: {str(e)}")
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                'imported': [],
                'errors': [f"Error al guardar en base de datos: {str(e)}"],
                'total': len(csv_data)
            }
        
        return {
            'imported': imported,
            'errors': errors,
            'total': len(csv_data)
        }
    
    @staticmethod
    def get_componentes_template():
        """Genera plantilla CSV para componentes"""
        template_data = {
            'nombre': ['Filtro de aceite motor', 'Pastillas de freno delanteras', 'Correa transmisión principal'],
            'descripcion': ['Filtro de aceite para motor diesel', 'Pastillas de freno para eje delantero', 'Correa de transmisión principal'],
            'numero_parte': ['FL-001', 'BK-002', 'BT-003'],
            'categoria': ['Filtros', 'Frenos', 'Transmisión'],
            'precio_unitario': ['25.50', '85.00', '150.75'],
            'stock_minimo': ['10', '5', '3'],
            'stock_actual': ['50', '20', '8'],
            'activo': ['True', 'True', 'True']
        }
        
        df = pd.DataFrame(template_data)
        
        # Crear CSV en memoria
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=plantilla_componentes.csv'
        
        return response