"""add posts model

Revision ID: 7808f8a75af5
Revises: ce4700aa7410
Create Date: 2022-04-01 09:32:55.721157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7808f8a75af5'
down_revision = 'ce4700aa7410'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('author', sa.String(length=255), nullable=True),
    sa.Column('date_posted', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('posts')
    # ### end Alembic commands ###
