"""empty message

Revision ID: 9a48b86b8856
Revises: 6b6aa97e1b29
Create Date: 2020-05-26 18:36:45.058031

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a48b86b8856'
down_revision = '6b6aa97e1b29'
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
