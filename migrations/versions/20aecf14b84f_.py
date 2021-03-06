"""empty message

Revision ID: 20aecf14b84f
Revises: fffe540a4324
Create Date: 2019-04-09 21:46:36.278746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20aecf14b84f'
down_revision = 'fffe540a4324'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Spots', sa.Column('rec_factors', sa.String(length=2000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Spots', 'rec_factors')
    # ### end Alembic commands ###
