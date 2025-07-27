# migrations/add_maintenance_table.py - Migración para tabla de mantenimiento
"""
Migración para crear la tabla de registros de mantenimiento
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'add_maintenance_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Crear tabla de registros de mantenimiento"""
    op.create_table(
        'registro_mantenimiento',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('maquina_id', sa.Integer(), nullable=False),
        sa.Column('componente_id', sa.Integer(), nullable=True),
        sa.Column('tipo_mantenimiento', sa.String(50), nullable=False),
        sa.Column('fecha_programada', sa.Date(), nullable=False),
        sa.Column('fecha_realizada', sa.Date(), nullable=True),
        sa.Column('estado', sa.String(20), nullable=False, default='programado'),
        sa.Column('prioridad', sa.String(20), nullable=False, default='normal'),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('tecnico_asignado', sa.String(100), nullable=True),
        sa.Column('costo_estimado', sa.Numeric(10, 2), nullable=True),
        sa.Column('costo_real', sa.Numeric(10, 2), nullable=True),
        sa.Column('tiempo_estimado_horas', sa.Integer(), nullable=True),
        sa.Column('tiempo_real_horas', sa.Integer(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('usuario_creacion_id', sa.Integer(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, default=datetime.now),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['maquina_id'], ['maquinas.ID'], ),
        sa.ForeignKeyConstraint(['componente_id'], ['componentes.ID'], ),
        sa.ForeignKeyConstraint(['usuario_creacion_id'], ['usuarios.ID'], )
    )
    
    # Crear índices para mejorar rendimiento
    op.create_index('idx_mantenimiento_fecha_programada', 'registro_mantenimiento', ['fecha_programada'])
    op.create_index('idx_mantenimiento_estado', 'registro_mantenimiento', ['estado'])
    op.create_index('idx_mantenimiento_maquina', 'registro_mantenimiento', ['maquina_id'])
    op.create_index('idx_mantenimiento_prioridad', 'registro_mantenimiento', ['prioridad'])

def downgrade():
    """Eliminar tabla de registros de mantenimiento"""
    op.drop_index('idx_mantenimiento_prioridad', table_name='registro_mantenimiento')
    op.drop_index('idx_mantenimiento_maquina', table_name='registro_mantenimiento')
    op.drop_index('idx_mantenimiento_estado', table_name='registro_mantenimiento')
    op.drop_index('idx_mantenimiento_fecha_programada', table_name='registro_mantenimiento')
    op.drop_table('registro_mantenimiento')
