"""
Modelo de Máquina
"""
from extensions import db
from .base_mixin import BaseModelMixin

# Tabla de asociación para relación many-to-many entre máquinas y componentes
maquinas_componentes = db.Table('maquinas_componentes',
    db.Column('maquina_id', db.Integer, db.ForeignKey('maquinas.id'), primary_key=True),
    db.Column('componente_id', db.Integer, db.ForeignKey('componentes.id'), primary_key=True),
    db.Column('cantidad_requerida', db.Integer, default=1),
    db.Column('es_critico', db.Boolean, default=False)
)

class Maquina(BaseModelMixin, db.Model):
    """Modelo para máquinas agrícolas"""
    __tablename__ = 'maquinas'
    
    # Información básica
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)
    
    codigo_maquina = db.Column(db.String(100), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    descripcion = db.Column(db.Text)
    tipo_maquina = db.Column(db.String(100), index=True)  # 'tractor', 'cosechadora', etc.
    
    # Información técnica
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    año_fabricacion = db.Column(db.Integer)
    numero_serie = db.Column(db.String(100), unique=True)
    
    # Especificaciones técnicas
    potencia = db.Column(db.String(50))  # ej: "150 HP"
    capacidad = db.Column(db.String(100))  # ej: "5000 L"
    especificaciones = db.Column(db.JSON)  # Especificaciones adicionales
    
    # Estado y ubicación
    estado = db.Column(db.String(50), default='operativa')  # 'operativa', 'mantenimiento', 'fuera_servicio'
    ubicacion = db.Column(db.String(200))
    
    # Información económica
    valor_adquisicion = db.Column(db.Numeric(12, 2))
    fecha_adquisicion = db.Column(db.Date)
    moneda = db.Column(db.String(3), default='USD')
    
    # Mantenimiento
    horas_trabajo = db.Column(db.Integer, default=0)
    ultima_revision = db.Column(db.Date)
    proxima_revision = db.Column(db.Date)
    
    # Archivos y multimedia
    foto = db.Column(db.String(255))
    manual_operacion = db.Column(db.String(255))
    documentos = db.Column(db.JSON)  # Array de documentos
    
    # Estado
    activa = db.Column(db.Boolean, default=True)
    
    # Relaciones
    componentes = db.relationship('Componente', 
                                secondary=maquinas_componentes,
                                backref=db.backref('maquinas', lazy='dynamic'),
                                lazy='dynamic')
    
    def __init__(self, codigo_maquina, nombre, **kwargs):
        self.codigo_maquina = codigo_maquina
        self.nombre = nombre
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def edad_años(self):
        """Calcula la edad de la máquina en años"""
        if self.año_fabricacion:
            from datetime import datetime
            return datetime.now().year - self.año_fabricacion
        return None
    
    @property
    def necesita_revision(self):
        """Verifica si la máquina necesita revisión"""
        if self.proxima_revision:
            from datetime import date
            return date.today() >= self.proxima_revision
        return False
    
    @property
    def componentes_criticos(self):
        """Obtiene los componentes críticos de la máquina"""
        return self.componentes.join(maquinas_componentes).filter(
            maquinas_componentes.c.es_critico == True
        )
    
    def agregar_componente(self, componente, cantidad=1, es_critico=False):
        """Agregar componente a la máquina"""
        if componente not in self.componentes:
            # Insertar en tabla de asociación con metadatos
            db.session.execute(
                maquinas_componentes.insert().values(
                    maquina_id=self.id,
                    componente_id=componente.id,
                    cantidad_requerida=cantidad,
                    es_critico=es_critico
                )
            )
            return True
        return False
    
    def remover_componente(self, componente):
        """Remover componente de la máquina"""
        if componente in self.componentes:
            self.componentes.remove(componente)
            return True
        return False
    
    def actualizar_horas_trabajo(self, horas_adicionales):
        """Actualizar horas de trabajo"""
        self.horas_trabajo += horas_adicionales
        
        # Si supera cierto umbral, programar revisión
        if self.horas_trabajo % 250 == 0:  # Cada 250 horas
            from datetime import date, timedelta
            self.proxima_revision = date.today() + timedelta(days=30)
    
    def to_dict(self):
        """Convertir a diccionario con información extendida"""
        data = super().to_dict()
        data.update({
            'edad_años': self.edad_años,
            'necesita_revision': self.necesita_revision,
            'cantidad_componentes': self.componentes.count(),
            'componentes_criticos_count': self.componentes_criticos.count()
        })
        return data
    
    @classmethod
    def buscar(cls, termino):
        """Buscar máquinas por término"""
        termino = f"%{termino}%"
        return cls.query.filter(
            db.or_(
                cls.nombre.ilike(termino),
                cls.codigo_maquina.ilike(termino),
                cls.marca.ilike(termino),
                cls.modelo.ilike(termino),
                cls.tipo_maquina.ilike(termino)
            )
        ).filter(cls.activa == True)
    
    @classmethod
    def por_tipo(cls, tipo):
        """Obtener máquinas por tipo"""
        return cls.query.filter(
            cls.tipo_maquina == tipo,
            cls.activa == True
        )
    
    @classmethod
    def necesitan_revision(cls):
        """Obtener máquinas que necesitan revisión"""
        from datetime import date
        return cls.query.filter(
            cls.proxima_revision <= date.today(),
            cls.activa == True
        )
    
    def __repr__(self):
        return f'<Maquina {self.codigo_maquina}: {self.nombre}>'
