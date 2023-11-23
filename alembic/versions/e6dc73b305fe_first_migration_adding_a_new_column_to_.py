"""first migration: adding a new column to catalog_table

Revision ID: e6dc73b305fe
Revises: 
Create Date: 2023-11-19 23:28:29.655424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6dc73b305fe'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("table_catalog") as batch_op:
        batch_op.add_column(sa.Column("TEST", sa.String()))


def downgrade() -> None:
    with op.batch_alter_table("table_catalog") as batch_op:
        batch_op.drop_column("TEST")

