"""empty message

Revision ID: 7bd1adcd9ae4
Revises: 37ccd417bd46
Create Date: 2023-10-04 01:49:54.532385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bd1adcd9ae4'
down_revision = '37ccd417bd46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('productOrder', schema=None) as batch_op:
        batch_op.drop_constraint('productOrder_user_id_fkey', type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('productOrder', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('productOrder_user_id_fkey', 'users', ['user_id'], ['user_id'])

    # ### end Alembic commands ###
