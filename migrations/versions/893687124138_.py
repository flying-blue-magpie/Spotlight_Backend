"""empty message

Revision ID: 893687124138
Revises: 20aecf14b84f
Create Date: 2019-04-13 07:48:32.093159

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '893687124138'
down_revision = '20aecf14b84f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Users', sa.Column('del_portrait', sa.String(length=100), nullable=True))
    op.add_column('Users', sa.Column('portrait_link', sa.String(length=255), nullable=True))
    op.drop_column('Users', 'portrait')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Users', sa.Column('portrait', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.drop_column('Users', 'portrait_link')
    op.drop_column('Users', 'del_portrait')
    # ### end Alembic commands ###