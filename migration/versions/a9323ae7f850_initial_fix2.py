"""Initial fix2

Revision ID: a9323ae7f850
Revises: 745048ba4f6e
Create Date: 2025-04-22 13:31:54.450448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9323ae7f850'
down_revision: Union[str, None] = '745048ba4f6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'visits', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'visits', type_='foreignkey')
    # ### end Alembic commands ###
