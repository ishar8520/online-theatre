"""Initial migration

Revision ID: 198a9266168f
Revises: 
Create Date: 2025-01-23 00:19:01.794661

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '198a9266168f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('create schema auth')
    op.create_table(
        'user',
        sa.Column('id', sa.UUID()),
        sa.Column('login', sa.TEXT()),
        sa.Column('password', sa.TEXT()),
        sa.Column('is_superuser', sa.BOOLEAN()),
        sa.Column('created', postgresql.TIMESTAMP(timezone=True)),
        sa.Column('modified', postgresql.TIMESTAMP(timezone=True)),
        sa.PrimaryKeyConstraint('id', name='user_pkey'),
        sa.UniqueConstraint('login', name='user_login_key'),
        schema='auth',
    )
    op.create_table(
        'role',
        sa.Column('id', sa.UUID()),
        sa.Column('name', sa.TEXT()),
        sa.Column('code', sa.TEXT()),
        sa.Column('created', postgresql.TIMESTAMP(timezone=True)),
        sa.Column('modified', postgresql.TIMESTAMP(timezone=True)),
        sa.PrimaryKeyConstraint('id', name='role_pkey'),
        sa.UniqueConstraint('code', name='role_code_key'),
        schema='auth',
    )
    op.create_table(
        'user_role',
        sa.Column('id', sa.UUID()),
        sa.Column('user_id', sa.UUID()),
        sa.Column('role_id', sa.UUID()),
        sa.Column('created', postgresql.TIMESTAMP(timezone=True)),
        sa.ForeignKeyConstraint(['role_id'], ['auth.role.id'], name='user_role_role_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], name='user_role_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='user_role_pkey'),
        sa.UniqueConstraint('user_id', 'role_id', name='uix_auth_role_id_user_id'),
        schema='auth',
    )
    op.create_table(
        'login_history',
        sa.Column('id', sa.UUID()),
        sa.Column('user_id', sa.UUID()),
        sa.Column('user_agent', sa.TEXT()),
        sa.Column('created', postgresql.TIMESTAMP(timezone=True)),
        sa.ForeignKeyConstraint(['user_id'], ['auth.user.id'], name='login_history_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='login_history_pkey'),
        schema='auth',
    )
    op.create_index(
        'ix_login_history_user_id',
        'login_history',
        ['user_id'],
        schema='auth',
    )


def downgrade() -> None:
    op.drop_index('ix_login_history_user_id', table_name='login_history', schema='auth')
    op.drop_table('login_history', schema='auth')
    op.drop_table('user_role', schema='auth')
    op.drop_table('role', schema='auth')
    op.drop_table('user', schema='auth')
    op.execute('drop schema auth')
