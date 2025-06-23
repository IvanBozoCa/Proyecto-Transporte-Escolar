"""Migración inicial

Revision ID: 682c803a9d82
Revises: 
Create Date: 2025-06-23 15:22:48.745295

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '682c803a9d82'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: elimina todas las tablas y restricciones previas."""

    # Primero, elimina tablas con relaciones dependientes
    op.drop_table('paradas_ruta_fija')
    op.drop_table('paradas')
    op.drop_table('rutas_estudiantes')
    op.drop_table('asistencias')
    op.drop_table('ubicaciones_conductor')
    op.drop_table('notificaciones')
    op.drop_table('vinculos_apoderado_conductor')
    op.drop_table('rutas')
    op.drop_table('rutas_fijas')
    op.drop_table('estudiantes')
    op.drop_table('direcciones')       # ← se elimina antes que conductores
    op.drop_table('conductores')       # ← ahora ya puedes eliminarla
    op.drop_table('acompanantes')
    op.drop_table('apoderados')
    op.drop_index(op.f('ix_usuarios_id_usuario'), table_name='usuarios')
    op.drop_table('usuarios')




def downgrade() -> None:
    """Downgrade schema (vacío en este caso)."""
    pass
