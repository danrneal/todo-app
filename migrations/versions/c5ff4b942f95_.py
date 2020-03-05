"""empty message

Revision ID: c5ff4b942f95
Revises: 5db8f223e74e
Create Date: 2020-03-05 15:10:25.250281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5ff4b942f95'
down_revision = '5db8f223e74e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('todo_lists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute('''
        INSERT INTO todo_lists (name)
        VALUES ('Uncategorized');
    ''')
    op.add_column('todos', sa.Column('list_id', sa.Integer(), nullable=True))
    op.execute('''
        UPDATE todos
           SET list_id = 1
         WHERE list_id IS NULL;
    ''')
    op.alter_column('todos', 'list_id', nullable=False)
    op.create_foreign_key(None, 'todos', 'todo_lists', ['list_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'todos', type_='foreignkey')
    op.drop_column('todos', 'list_id')
    op.drop_table('todo_lists')
    # ### end Alembic commands ###
