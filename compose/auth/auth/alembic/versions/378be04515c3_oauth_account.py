"""oauth_account

Revision ID: 378be04515c3
Revises: 917d74037842
Create Date: 2025-01-30 13:46:46.696996

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '378be04515c3'
down_revision: Union[str, None] = '917d74037842'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'oauth_account',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('oauth_name', sa.TEXT(), nullable=False),
        sa.Column('access_token', sa.TEXT(), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=True),
        sa.Column('refresh_token', sa.TEXT(), nullable=True),
        sa.Column('account_id', sa.TEXT(), nullable=False),
        sa.Column('account_email', sa.TEXT(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['auth.user.id'],
            name=op.f('fk_oauth_account_user_id_user'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_oauth_account')),
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_oauth_account_account_id'),
        'oauth_account',
        ['account_id'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_oauth_account_oauth_name'),
        'oauth_account',
        ['oauth_name'],
        unique=False,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_oauth_account_user_id'),
        'oauth_account',
        ['user_id'],
        unique=False,
        schema='auth',
    )

    op.alter_column(
        'login_history',
        'user_agent',
        existing_type=sa.TEXT(),
        nullable=False,
        schema='auth',
    )
    op.drop_constraint(
        'login_history_user_id_fkey',
        'login_history',
        type_='foreignkey',
        schema='auth',
    )
    op.create_foreign_key(
        op.f('fk_login_history_user_id_user'),
        'login_history',
        'user',
        ['user_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth',
    )

    op.add_column(
        'user',
        sa.Column('email', sa.TEXT(), nullable=True),
        schema='auth',
    )
    op.alter_column(
        'user',
        'login',
        existing_type=sa.TEXT(),
        nullable=True,
        schema='auth',
    )
    op.alter_column(
        'user',
        'password',
        existing_type=sa.TEXT(),
        nullable=True,
        schema='auth',
    )

    op.drop_constraint(
        'uq_user_login',
        'user',
        type_='unique',
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_user_email'),
        'user',
        ['email'],
        unique=True,
        schema='auth',
    )
    op.create_index(
        op.f('ix_auth_user_login'),
        'user',
        ['login'],
        unique=True,
        schema='auth',
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_auth_user_login'),
        table_name='user',
        schema='auth',
    )
    op.drop_index(
        op.f('ix_auth_user_email'),
        table_name='user',
        schema='auth',
    )
    op.create_unique_constraint(
        'uq_user_login',
        'user',
        ['login'],
        schema='auth',
    )

    op.alter_column(
        'user',
        'password',
        existing_type=sa.TEXT(),
        nullable=False,
        schema='auth',
    )
    op.alter_column(
        'user',
        'login',
        existing_type=sa.TEXT(),
        nullable=False,
        schema='auth',
    )
    op.drop_column(
        'user',
        'email',
        schema='auth',
    )

    op.drop_constraint(
        op.f('fk_login_history_user_id_user'),
        'login_history',
        type_='foreignkey',
        schema='auth',
    )
    op.create_foreign_key(
        'login_history_user_id_fkey',
        'login_history',
        'user',
        ['user_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth',
    )
    op.alter_column(
        'login_history',
        'user_agent',
        existing_type=sa.TEXT(),
        nullable=True,
        schema='auth',
    )

    op.drop_index(op.f('ix_auth_oauth_account_user_id'), table_name='oauth_account', schema='auth')
    op.drop_index(op.f('ix_auth_oauth_account_oauth_name'), table_name='oauth_account', schema='auth')
    op.drop_index(op.f('ix_auth_oauth_account_account_id'), table_name='oauth_account', schema='auth')
    op.drop_table('oauth_account', schema='auth')
