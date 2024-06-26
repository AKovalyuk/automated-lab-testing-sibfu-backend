"""Remove image_id from Practice

Revision ID: f4c11061bb6d
Revises: be6925e77a6e
Create Date: 2024-05-14 15:48:45.981562

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4c11061bb6d'
down_revision: Union[str, None] = 'be6925e77a6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('practice', 'image_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('practice', sa.Column('image_id', sa.UUID(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
