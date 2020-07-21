"""empty message

Revision ID: 648731ac1449
Revises: 425500be663f
Create Date: 2020-07-21 01:09:31.827728

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '648731ac1449'
down_revision = '425500be663f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('PortfolioMaster', 'gains',
               existing_type=sa.REAL(),
               type_=sa.Numeric(),
               existing_nullable=False)
    op.alter_column('PortfolioMaster', 'invested',
               existing_type=sa.REAL(),
               type_=sa.Numeric(),
               existing_nullable=True)
    op.alter_column('PortfolioMaster', 'losses',
               existing_type=sa.REAL(),
               type_=sa.Numeric(),
               existing_nullable=False)
    op.alter_column('PortfolioMaster', 'weight',
               existing_type=sa.REAL(),
               type_=sa.Numeric(),
               existing_nullable=False)
    op.alter_column('PortfolioMaster', 'withdrawls',
               existing_type=sa.REAL(),
               type_=sa.Numeric(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('PortfolioMaster', 'withdrawls',
               existing_type=sa.Numeric(),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('PortfolioMaster', 'weight',
               existing_type=sa.Numeric(),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('PortfolioMaster', 'losses',
               existing_type=sa.Numeric(),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('PortfolioMaster', 'invested',
               existing_type=sa.Numeric(),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('PortfolioMaster', 'gains',
               existing_type=sa.Numeric(),
               type_=sa.REAL(),
               existing_nullable=False)
    # ### end Alembic commands ###
