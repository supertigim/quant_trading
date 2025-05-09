"""merge heads

Revision ID: 2a1092c29178
Revises: bd1f6664ae95, change_stock_id_to_uuid
Create Date: 2025-05-09 18:55:50.447667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a1092c29178'
down_revision: Union[str, None] = ('bd1f6664ae95', 'change_stock_id_to_uuid')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 