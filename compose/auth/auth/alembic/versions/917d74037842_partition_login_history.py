"""partition login history

Revision ID: 917d74037842
Revises: 198a9266168f
Create Date: 2025-01-27 21:53:50.527881

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "917d74037842"
down_revision: Union[str, None] = "198a9266168f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "login_history",
        sa.Column("id", sa.UUID()),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("user_agent", sa.TEXT()),
        sa.Column("created", postgresql.TIMESTAMP(timezone=True)),
        sa.ForeignKeyConstraint(
            ["user_id"], ["auth.user.id"], name="login_history_user_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", "created", name="login_history_pkey"),
        schema="auth",
        postgresql_partition_by="RANGE (created)",
    )
    op.execute(
        """
        CREATE TABLE login_history_january PARTITION OF auth.login_history
            FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
    """
    )

    op.execute(
        """
        CREATE TABLE login_history_february PARTITION OF auth.login_history
            FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
    """
    )

    op.execute(
        """
        CREATE TABLE login_history_march PARTITION OF auth.login_history
            FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
    """
    )

    op.execute(
        """
        CREATE TABLE login_history_april PARTITION OF auth.login_history
            FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
    """
    )

    op.create_index(
        "ix_login_history_user_id",
        "login_history",
        ["user_id", "created"],
        schema="auth",
    )


def downgrade():
    op.drop_index("ix_login_history_user_id", table_name="login_history", schema="auth")
    op.drop_table("login_history", schema="auth")
    op.drop_table("login_history_april", schema="auth")
    op.drop_table("login_history_march", schema="auth")
    op.drop_table("login_history_february", schema="auth")
    op.drop_table("login_history_january", schema="auth")
