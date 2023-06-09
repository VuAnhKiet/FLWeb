"""add fname column for model and image class

Revision ID: 0ebd5d25281d
Revises: 529e2ea59472
Create Date: 2023-06-08 16:46:34.559614

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ebd5d25281d'
down_revision = '529e2ea59472'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fname', sa.String(length=50), nullable=True))

    with op.batch_alter_table('model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fname', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('model', schema=None) as batch_op:
        batch_op.drop_column('fname')

    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.drop_column('fname')

    # ### end Alembic commands ###
