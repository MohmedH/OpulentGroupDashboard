"""empty message

Revision ID: 425500be663f
Revises: ee90ed45fc44
Create Date: 2020-07-21 01:08:10.289281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '425500be663f'
down_revision = 'ee90ed45fc44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('PortfolioMaster', 'total',
               existing_type=sa.REAL(),
               type_=sa.Numeric(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('PortfolioMaster', 'total',
               existing_type=sa.Numeric(),
               type_=sa.REAL(),
               existing_nullable=False)
    # ### end Alembic commands ###
