"""empty message

Revision ID: bb598b183353
Revises: 5be3bbb17286
Create Date: 2020-07-21 00:12:49.479479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb598b183353'
down_revision = '5be3bbb17286'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('PartnersGainsAndLoss', sa.Column('calcWeight', sa.REAL(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('PartnersGainsAndLoss', 'calcWeight')
    # ### end Alembic commands ###
