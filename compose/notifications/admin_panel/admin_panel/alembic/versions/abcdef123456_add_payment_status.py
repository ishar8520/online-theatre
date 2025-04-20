"""Insert payment_status system template

Revision ID: abcdef123456
Revises: 123456789abc
Create Date: 2025-04-20 16:00:00.000000

"""
import uuid
import datetime
from alembic import op
import sqlalchemy as sa

revision = 'abcdef123456'
down_revision = '123456789abc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    templates_table = sa.table(
        'templates',
        sa.Column('id', sa.UUID(as_uuid=True)),
        sa.Column('code', sa.String(length=100)),
        sa.Column('subject', sa.String(length=255)),
        sa.Column('body', sa.Text()),
        sa.Column(
            'type',
            sa.Enum('EMAIL', 'SMS', 'PUSH', 'OTHER', name='template_type_enum')
        ),
        sa.Column('is_system', sa.Boolean()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        schema='admin_panel',
    )

    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    op.bulk_insert(
        templates_table,
        [
            {
                'id': uuid.UUID('5e6930f9-1f04-4cff-a410-49cdfc5a9c50'),
                'code': 'payment_status',
                'subject': 'PAYMENT STATUS',
                'body': 'Платеж {{ payment_status }}',
                'type': 'EMAIL',
                'is_system': True,
                'created_at': now,
                'updated_at': now,
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM admin_panel.templates
        WHERE code = 'payment_status'
        """
    )
