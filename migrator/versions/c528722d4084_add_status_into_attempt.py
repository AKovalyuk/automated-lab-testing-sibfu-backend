"""Add status into attempt

Revision ID: c528722d4084
Revises: ccd3fd9d47fc
Create Date: 2024-04-20 21:37:08.691420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c528722d4084'
down_revision: Union[str, None] = 'ccd3fd9d47fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attempt', sa.Column('status', sa.String(length=50), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('attempt', 'status')
    # ### end Alembic commands ###