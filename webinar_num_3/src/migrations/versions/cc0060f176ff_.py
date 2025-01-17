"""empty message

Revision ID: cc0060f176ff
Revises: 
Create Date: 2022-07-26 15:26:46.528321

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'cc0060f176ff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('denylist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('jti', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_denylist_id'), 'denylist', ['id'], unique=False)
    op.create_table('users',
    sa.Column('userid', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), server_default='f', nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('userid')
    )
    op.create_index(op.f('ix_users_userid'), 'users', ['userid'], unique=False)
    op.create_table('validtokens',
    sa.Column('access_token', sa.String(), nullable=False),
    sa.Column('jti_a', sa.String(), nullable=True),
    sa.Column('refresh_token', sa.String(), nullable=True),
    sa.Column('jti_r', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('access_token')
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('views', sa.Integer(), server_default='0', nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.userid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_id'), 'post', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_post_id'), table_name='post')
    op.drop_table('post')
    op.drop_table('validtokens')
    op.drop_index(op.f('ix_users_userid'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_denylist_id'), table_name='denylist')
    op.drop_table('denylist')
    # ### end Alembic commands ###
