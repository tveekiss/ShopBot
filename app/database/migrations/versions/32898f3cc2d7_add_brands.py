"""add brands

Revision ID: 32898f3cc2d7
Revises: c4846fff8b85
Create Date: 2024-05-25 15:19:55.514278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32898f3cc2d7'
down_revision: Union[str, None] = 'c4846fff8b85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('brands',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('category', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('users')
    op.add_column('items', sa.Column('brand', sa.Integer(), nullable=False))
    op.drop_constraint('items_category_fkey', 'items', type_='foreignkey')
    op.create_foreign_key(None, 'items', 'brands', ['brand'], ['id'])
    op.drop_column('items', 'category')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('category', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'items', type_='foreignkey')
    op.create_foreign_key('items_category_fkey', 'items', 'categories', ['category'], ['id'])
    op.drop_column('items', 'brand')
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('tg_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('tg_id', name='users_tg_id_key')
    )
    op.drop_table('brands')
    # ### end Alembic commands ###