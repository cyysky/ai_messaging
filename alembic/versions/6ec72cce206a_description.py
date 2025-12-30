"""description

Revision ID: 6ec72cce206a
Revises: 753d9557b07b
Create Date: 2025-12-31 00:50:37.569126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ec72cce206a'
down_revision: Union[str, None] = '753d9557b07b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
