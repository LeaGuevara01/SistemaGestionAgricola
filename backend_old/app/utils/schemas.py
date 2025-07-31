"""
Schemas de validación con Marshmallow para el sistema de gestión agrícola
"""
from marshmallow import Schema, fields, validate, ValidationError, post_load, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime
from typing import Dict, Any


class BaseSchema(Schema):
    """Schema base con configuraciones comunes"""
    
    class Meta:
        # Incluir campos desconocidos como errores
        unknown = EXCLUDE
        # Formato de fecha por defecto
        dateformat = '%Y-%m-%d'
        datetimeformat = '%Y-%m-%dT%H:%M:%S'
    
    @post_load
    def strip_strings(self, data, **kwargs):
        """Limpiar strings de espacios en blanco"""
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()
        return data


class ComponenteSchema(BaseSchema):
    """Schema para validación de componentes"""
    
    id = fields.Integer(dump_only=True)
    nombre = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'El nombre del componente es obligatorio'}
    )
    descripcion = fields.String(
        validate=validate.Length(max=500),
        allow_none=True
    )
    precio_unitario = fields.Decimal(
        required=True,
        validate=validate.Range(min=0),
        error_messages={'required': 'El precio unitario es obligatorio'}
    )
    categoria = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    fabricante = fields.String(
        validate=validate.Length(max=100),
        allow_none=True
    )
    numero_parte = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    peso = fields.Decimal(
        validate=validate.Range(min=0),
        allow_none=True
    )
    dimensiones = fields.String(
        validate=validate.Length(max=100),
        allow_none=True
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class MaquinaSchema(BaseSchema):
    """Schema para validación de máquinas"""
    
    id = fields.Integer(dump_only=True)
    nombre = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'El nombre de la máquina es obligatorio'}
    )
    tipo = fields.String(
        validate=validate.OneOf(['Cosechadora', 'Tractor', 'Sembradora', 'Pulverizadora', 'Otro']),
        allow_none=True
    )
    marca = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    modelo = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    año = fields.Integer(
        validate=validate.Range(min=1950, max=datetime.now().year + 1),
        allow_none=True
    )
    numero_serie = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    horas_trabajo = fields.Decimal(
        validate=validate.Range(min=0),
        allow_none=True
    )
    estado = fields.String(
        validate=validate.OneOf(['Operativo', 'Mantenimiento', 'Fuera de Servicio']),
        missing='Operativo'
    )
    ubicacion = fields.String(
        validate=validate.Length(max=100),
        allow_none=True
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProveedorSchema(BaseSchema):
    """Schema para validación de proveedores"""
    
    id = fields.Integer(dump_only=True)
    nombre = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'El nombre del proveedor es obligatorio'}
    )
    contacto = fields.String(
        validate=validate.Length(max=100),
        allow_none=True
    )
    telefono = fields.String(
        validate=validate.Length(max=20),
        allow_none=True
    )
    email = fields.Email(allow_none=True)
    direccion = fields.String(
        validate=validate.Length(max=200),
        allow_none=True
    )
    ciudad = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    pais = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    activo = fields.Boolean(missing=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class CompraSchema(BaseSchema):
    """Schema para validación de compras"""
    
    id = fields.Integer(dump_only=True)
    componente_id = fields.Integer(
        required=True,
        error_messages={'required': 'El ID del componente es obligatorio'}
    )
    proveedor_id = fields.Integer(
        required=True,
        error_messages={'required': 'El ID del proveedor es obligatorio'}
    )
    cantidad = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={'required': 'La cantidad es obligatoria'}
    )
    precio_unitario = fields.Decimal(
        required=True,
        validate=validate.Range(min=0),
        error_messages={'required': 'El precio unitario es obligatorio'}
    )
    total = fields.Decimal(dump_only=True)
    fecha_compra = fields.Date(
        required=True,
        error_messages={'required': 'La fecha de compra es obligatoria'}
    )
    fecha_entrega = fields.Date(allow_none=True)
    numero_factura = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    estado = fields.String(
        validate=validate.OneOf(['Pendiente', 'Entregado', 'Cancelado']),
        missing='Pendiente'
    )
    notas = fields.String(
        validate=validate.Length(max=500),
        allow_none=True
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class StockSchema(BaseSchema):
    """Schema para validación de stock"""
    
    id = fields.Integer(dump_only=True)
    componente_id = fields.Integer(
        required=True,
        error_messages={'required': 'El ID del componente es obligatorio'}
    )
    cantidad_actual = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        error_messages={'required': 'La cantidad actual es obligatoria'}
    )
    cantidad_minima = fields.Integer(
        validate=validate.Range(min=0),
        missing=0
    )
    ubicacion = fields.String(
        validate=validate.Length(max=100),
        allow_none=True
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class MaquinaComponenteSchema(BaseSchema):
    """Schema para validación de relación máquina-componente"""
    
    id = fields.Integer(dump_only=True)
    maquina_id = fields.Integer(
        required=True,
        error_messages={'required': 'El ID de la máquina es obligatorio'}
    )
    componente_id = fields.Integer(
        required=True,
        error_messages={'required': 'El ID del componente es obligatorio'}
    )
    cantidad_requerida = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={'required': 'La cantidad requerida es obligatoria'}
    )
    fecha_instalacion = fields.Date(allow_none=True)
    fecha_proximo_cambio = fields.Date(allow_none=True)
    observaciones = fields.String(
        validate=validate.Length(max=500),
        allow_none=True
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class BusquedaSchema(BaseSchema):
    """Schema para validación de parámetros de búsqueda"""
    
    q = fields.String(
        validate=validate.Length(min=1, max=100),
        allow_none=True
    )
    page = fields.Integer(
        validate=validate.Range(min=1),
        missing=1
    )
    per_page = fields.Integer(
        validate=validate.Range(min=1, max=100),
        missing=20
    )
    sort_by = fields.String(
        validate=validate.Length(max=50),
        allow_none=True
    )
    sort_order = fields.String(
        validate=validate.OneOf(['asc', 'desc']),
        missing='asc'
    )


class FiltroFechaSchema(BaseSchema):
    """Schema para validación de filtros de fecha"""
    
    fecha_inicio = fields.Date(allow_none=True)
    fecha_fin = fields.Date(allow_none=True)
    
    def validate_fechas(self, data, **kwargs):
        """Validar que fecha_inicio sea menor que fecha_fin"""
        if data.get('fecha_inicio') and data.get('fecha_fin'):
            if data['fecha_inicio'] > data['fecha_fin']:
                raise ValidationError('La fecha de inicio debe ser menor que la fecha de fin')


class ErrorResponseSchema(BaseSchema):
    """Schema para respuestas de error estandarizadas"""
    
    error = fields.Boolean(missing=True)
    message = fields.String(required=True)
    error_code = fields.String(allow_none=True)
    status_code = fields.Integer(required=True)
    field_errors = fields.Dict(allow_none=True)
    timestamp = fields.DateTime(missing=datetime.utcnow)


class SuccessResponseSchema(BaseSchema):
    """Schema para respuestas exitosas estandarizadas"""
    
    success = fields.Boolean(missing=True)
    message = fields.String(allow_none=True)
    data = fields.Raw(allow_none=True)
    timestamp = fields.DateTime(missing=datetime.utcnow)


# Instancias de schemas para reutilización
componente_schema = ComponenteSchema()
componentes_schema = ComponenteSchema(many=True)

maquina_schema = MaquinaSchema()
maquinas_schema = MaquinaSchema(many=True)

proveedor_schema = ProveedorSchema()
proveedores_schema = ProveedorSchema(many=True)

compra_schema = CompraSchema()
compras_schema = CompraSchema(many=True)

stock_schema = StockSchema()
stocks_schema = StockSchema(many=True)

maquina_componente_schema = MaquinaComponenteSchema()
maquinas_componentes_schema = MaquinaComponenteSchema(many=True)

busqueda_schema = BusquedaSchema()
filtro_fecha_schema = FiltroFechaSchema()
error_response_schema = ErrorResponseSchema()
success_response_schema = SuccessResponseSchema()
