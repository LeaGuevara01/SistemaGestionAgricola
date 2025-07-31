"""
Servicio para manejar metadatos de campos de forma dinámica
Detecta automáticamente los campos de la BD y define sus propiedades
"""
from ..utils.db import db
from sqlalchemy import inspect

class FieldMetadataService:
    
    @staticmethod
    def get_table_fields(table_name):
        """Obtiene todos los campos reales de una tabla"""
        try:
            inspector = inspect(db.engine)
            columns = inspector.get_columns(table_name)
            
            fields = []
            for col in columns:
                field_info = {
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'primary_key': col.get('primary_key', False),
                    'autoincrement': col.get('autoincrement', False)
                }
                fields.append(field_info)
            
            return fields
        except Exception as e:
            print(f"Error obteniendo campos de {table_name}: {e}")
            return []
    
    @staticmethod
    def get_maquinas_metadata():
        """Metadatos específicos para máquinas con mapeo frontend-backend"""
        
        # Obtener campos reales de la BD
        db_fields = FieldMetadataService.get_table_fields('maquinas')
        db_field_names = [f['name'] for f in db_fields]
        
        # Definir metadatos con mapeo frontend -> backend
        field_metadata = {
            # Campos que SÍ existen en la BD
            'nombre': {
                'db_field': 'Nombre',
                'exists_in_db': 'Nombre' in db_field_names,
                'type': 'text',
                'required': True,
                'label': 'Nombre de la Máquina',
                'placeholder': 'Ej: Tractor John Deere'
            },
            'codigo': {
                'db_field': 'Codigo', 
                'exists_in_db': 'Codigo' in db_field_names,
                'type': 'text',
                'required': True,
                'label': 'Código',
                'placeholder': 'Ej: M-001'
            },
            'marca': {
                'db_field': 'Marca',
                'exists_in_db': 'Marca' in db_field_names,
                'type': 'text',
                'required': False,
                'label': 'Marca',
                'placeholder': 'Ej: John Deere'
            },
            'modelo': {
                'db_field': 'Modelo',
                'exists_in_db': 'Modelo' in db_field_names,
                'type': 'text',
                'required': False,
                'label': 'Modelo',
                'placeholder': 'Ej: 6110M'
            },
            'año': {
                'db_field': 'Año',
                'exists_in_db': 'Año' in db_field_names,
                'type': 'number',
                'required': False,
                'label': 'Año',
                'placeholder': 'Ej: 2020',
                'min': 1900,
                'max': 2030
            },
            'estado': {
                'db_field': 'Estado',
                'exists_in_db': 'Estado' in db_field_names,
                'type': 'select',
                'required': False,
                'label': 'Estado',
                'options': [
                    {'value': 'Operativa', 'label': 'Operativa'},
                    {'value': 'Mantenimiento', 'label': 'En Mantenimiento'},
                    {'value': 'Fuera de Servicio', 'label': 'Fuera de Servicio'},
                    {'value': 'Inactiva', 'label': 'Inactiva'}
                ]
            },
            'observaciones': {
                'db_field': 'Observaciones',
                'exists_in_db': 'Observaciones' in db_field_names,
                'type': 'textarea',
                'required': False,
                'label': 'Observaciones',
                'placeholder': 'Notas adicionales sobre la máquina'
            },
            'foto': {
                'db_field': 'Foto',
                'exists_in_db': 'Foto' in db_field_names,
                'type': 'file',
                'required': False,
                'label': 'Foto',
                'accept': 'image/*'
            },
            
            # Campos que NO existen en la BD actual (para compatibilidad con frontend)
            'numero_serie': {
                'db_field': 'Numero_Serie',
                'exists_in_db': False,  # No existe en BD actual
                'type': 'text',
                'required': False,
                'label': 'Número de Serie',
                'placeholder': 'Número de serie del fabricante',
                'note': 'Campo no disponible en BD actual'
            },
            'tipo': {
                'db_field': 'Tipo',
                'exists_in_db': False,  # No existe en BD actual
                'type': 'select',
                'required': False,
                'label': 'Tipo de Máquina',
                'options': [
                    {'value': 'Tractor', 'label': 'Tractor'},
                    {'value': 'Cosechadora', 'label': 'Cosechadora'},
                    {'value': 'Arado', 'label': 'Arado'},
                    {'value': 'Sembradora', 'label': 'Sembradora'},
                    {'value': 'Pulverizadora', 'label': 'Pulverizadora'}
                ],
                'note': 'Campo no disponible en BD actual'
            },
            'horas_trabajo': {
                'db_field': 'Horas_Trabajo',
                'exists_in_db': False,  # No existe en BD actual
                'type': 'number',
                'required': False,
                'label': 'Horas de Trabajo',
                'placeholder': '0',
                'min': 0,
                'note': 'Campo no disponible en BD actual'
            },
            'ubicacion': {
                'db_field': 'Ubicacion',
                'exists_in_db': False,  # No existe en BD actual
                'type': 'text',
                'required': False,
                'label': 'Ubicación Actual',
                'placeholder': 'Ej: Campo Norte, Galpón 2',
                'note': 'Campo no disponible en BD actual'
            }
        }
        
        return {
            'db_fields': db_fields,
            'field_metadata': field_metadata,
            'available_fields': [k for k, v in field_metadata.items() if v['exists_in_db']],
            'unavailable_fields': [k for k, v in field_metadata.items() if not v['exists_in_db']]
        }
    
    @staticmethod
    def get_componentes_metadata():
        """Metadatos específicos para componentes"""
        
        # Obtener campos reales de la BD
        db_fields = FieldMetadataService.get_table_fields('componentes')
        db_field_names = [f['name'] for f in db_fields]
        
        field_metadata = {
            'nombre': {
                'db_field': 'Nombre',
                'exists_in_db': 'Nombre' in db_field_names,
                'type': 'text',
                'required': True,
                'label': 'Nombre del Componente'
            },
            'descripcion': {
                'db_field': 'Descripcion',
                'exists_in_db': 'Descripcion' in db_field_names,
                'type': 'textarea',
                'required': False,
                'label': 'Descripción'
            },
            'numero_parte': {
                'db_field': 'ID_Componente',
                'exists_in_db': 'ID_Componente' in db_field_names,
                'type': 'text',
                'required': False,
                'label': 'Número de Parte'
            },
            'categoria': {
                'db_field': 'Tipo',
                'exists_in_db': 'Tipo' in db_field_names,
                'type': 'select',
                'required': False,
                'label': 'Categoría',
                'options': [
                    {'value': 'Motor', 'label': 'Motor'},
                    {'value': 'Transmision', 'label': 'Transmisión'},
                    {'value': 'Hidraulico', 'label': 'Hidráulico'},
                    {'value': 'Neumatico', 'label': 'Neumático'},
                    {'value': 'Electrico', 'label': 'Eléctrico'},
                    {'value': 'Filtro', 'label': 'Filtro'},
                    {'value': 'Lubricante', 'label': 'Lubricante'}
                ]
            },
            'precio_unitario': {
                'db_field': 'Precio',
                'exists_in_db': 'Precio' in db_field_names,
                'type': 'number',
                'required': False,
                'label': 'Precio Unitario',
                'min': 0,
                'step': 0.01
            },
            'marca': {
                'db_field': 'Marca',
                'exists_in_db': 'Marca' in db_field_names,
                'type': 'text',
                'required': False,
                'label': 'Marca'
            },
            'modelo': {
                'db_field': 'Modelo',
                'exists_in_db': 'Modelo' in db_field_names,
                'type': 'text',
                'required': False,
                'label': 'Modelo'
            },
            'foto': {
                'db_field': 'Foto',
                'exists_in_db': 'Foto' in db_field_names,
                'type': 'file',
                'required': False,
                'label': 'Foto',
                'accept': 'image/*'
            }
        }
        
        return {
            'db_fields': db_fields,
            'field_metadata': field_metadata,
            'available_fields': [k for k, v in field_metadata.items() if v['exists_in_db']],
            'unavailable_fields': [k for k, v in field_metadata.items() if not v['exists_in_db']]
        }
