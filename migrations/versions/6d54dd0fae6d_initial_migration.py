"""Initial migration

Revision ID: 6d54dd0fae6d
Revises: a71ded894faa
Create Date: 2017-08-14 16:09:35.673003

"""

# revision identifiers, used by Alembic.
revision = '6d54dd0fae6d'
down_revision = 'a71ded894faa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'users_ibfk_1', 'users', type_='foreignkey')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(u'users_ibfk_1', 'users', 'roles', ['role_id'], ['id'])
    ### end Alembic commands ###