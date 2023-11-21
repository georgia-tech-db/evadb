"""edit a column in table_catalog

Revision ID: b0ecb091fa7b
Revises: e6dc73b305fe
Create Date: 2023-11-20 19:01:31.602478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0ecb091fa7b'
down_revision: Union[str, None] = 'e6dc73b305fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("table_catalog") as batch_op:
        batch_op.alter_column("TEST", new_column_name="TEST1")


def downgrade() -> None:
    with op.batch_alter_table("table_catalog") as batch_op:
        batch_op.alter_column("TEST1", new_column_name="TEST")