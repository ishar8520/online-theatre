"""Insert default system templates

Revision ID: 123456789abc
Revises: 21c108021419
Create Date: 2025-03-23 13:30:00.000000

"""
import uuid
import datetime
from alembic import op
import sqlalchemy as sa

revision = '123456789abc'
down_revision = '21c108021419'
branch_labels = None
depends_on = None


def upgrade() -> None:
    templates_table = sa.table(
        'templates',
        sa.Column('id', sa.UUID(as_uuid=True)),
        sa.Column('code', sa.String(length=100)),
        sa.Column('subject', sa.String(length=255)),
        sa.Column('body', sa.Text()),
        sa.Column('type', sa.Enum('EMAIL', 'SMS', 'PUSH', 'OTHER', name='template_type_enum')),
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
                'id': uuid.uuid4(),
                'code': 'registration',
                'subject': 'Подтверждение регистрации',
                'body': 'Привет {{ name }}!!! Спешим поздравить с успешной регистрацией на online-theatre. '
                        'Для подтверждения своей почты пожалуйста перейди по ссылке {{ short_link }}',
                'type': 'EMAIL',
                'is_system': True,
                'created_at': now,
                'updated_at': now,
            },
            {
                'id': uuid.uuid4(),
                'code': 'on_new_movie',
                'subject': 'Вышла новая серия',
                'body': 'Привет {{ name }}!!! Вышла новая серия {{ content_id }}! Бегом смотреть на online-theatre!',
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
        WHERE code IN ('registration', 'on_new_movie')
        """
    )
