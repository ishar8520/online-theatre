"""oauth_account

Revision ID: 3c9d17ab4206
Revises: 378be04515c3
Create Date: 2025-01-31 17:51:39.332860

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3c9d17ab4206'
down_revision: Union[str, None] = '378be04515c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        op.f('uq_oauth_account_oauth_name'),
        'oauth_account',
        ['oauth_name', 'account_id'],
        schema='auth',
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq_oauth_account_oauth_name'),
        'oauth_account',
        type_='unique',
        schema='auth',
    )
