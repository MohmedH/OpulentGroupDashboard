"""empty message

Revision ID: 5aa505f63d73
Revises: 9a48b86b8856
Create Date: 2020-05-26 19:08:14.320607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5aa505f63d73'
down_revision = '9a48b86b8856'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'name')
    # ### end Alembic commands ###
