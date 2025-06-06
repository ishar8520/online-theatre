"""Initial migration

Revision ID: 27ecd0bc2cab
Revises: 
Create Date: 2025-04-15 23:06:43.935054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27ecd0bc2cab'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA billing')

    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('ps_name', sa.Text(), nullable=True),
    sa.Column('ps_invoice_id', sa.UUID(), nullable=True),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_payment')),
    schema='billing'
    )
    op.create_table('purchase_item',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('payment_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('type', sa.Text(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['payment_id'], ['billing.payment.id'], name=op.f('fk_purchase_item_payment_id_payment'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_purchase_item')),
    schema='billing'
    )
    op.create_table('purchase_item_property',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('purchase_item_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('code', sa.Text(), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['purchase_item_id'], ['billing.purchase_item.id'], name=op.f('fk_purchase_item_property_purchase_item_id_purchase_item'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_purchase_item_property')),
    sa.UniqueConstraint('purchase_item_id', 'code', name=op.f('uq_purchase_item_property_purchase_item_id')),
    schema='billing'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('purchase_item_property', schema='billing')
    op.drop_table('purchase_item', schema='billing')
    op.drop_table('payment', schema='billing')
    # ### end Alembic commands ###
