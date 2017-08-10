"""Initial migration

Revision ID: a71ded894faa
Revises: 4a006b7cc0a1
Create Date: 2017-08-10 18:03:44.965754

"""

# revision identifiers, used by Alembic.
revision = 'a71ded894faa'
down_revision = '4a006b7cc0a1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('login_log', sa.Column('login_browser', sa.String(length=200), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('login_log', 'login_browser')
    ### end Alembic commands ###
