"""empty message

Revision ID: 36743df1ea0a
Revises: 75b32f2bcd87
Create Date: 2020-07-14 19:01:55.156177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36743df1ea0a'
down_revision = '75b32f2bcd87'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Users_Graveyard',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userID', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.Binary(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('deleted_at', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('userID')
    )
    op.add_column('User', sa.Column('created_at', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'created_at')
    op.drop_table('Users_Graveyard')
    # ### end Alembic commands ###