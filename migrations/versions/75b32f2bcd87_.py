"""empty message

Revision ID: 75b32f2bcd87
Revises: 98118f485a60
Create Date: 2020-07-13 00:05:26.156797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75b32f2bcd87'
down_revision = '98118f485a60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('PortfolioMaster', sa.Column('weight', sa.REAL(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('PortfolioMaster', 'weight')
    # ### end Alembic commands ###
