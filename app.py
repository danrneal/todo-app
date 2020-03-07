"""A todo app built in flask with a postgresql db"""

import sys
from flask import (
    Flask, render_template, request, jsonify, abort, redirect, url_for
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

DIALECT = 'postgresql'
USER = 'dneal'
PASS = ''
HOST = 'localhost'
PORT = 5432
DATABASE = 'todoapp'

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = f'{DIALECT}://{USER}:{PASS}@{HOST}:{PORT}/{DATABASE}'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todo(db.Model):
    """A model representing a todo item

    Attributes:
        id: A unique identifier for a todo object
        description: A str representing the todo object's content
        list_id: A foreign key linking a todo item to a todo list
    """
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(
        db.Integer,
        db.ForeignKey('todo_lists.id'),
        nullable=False
    )

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


class TodoList(db.Model):
    """A model representing a todo list

    Attibutes:
        id: A unique identifier for a todo list object
        name: A str representing the todo list object's name
        todos: A relationship for a foreign key on the todo item model
    """
    __tablename__ = 'todo_lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship(
        'Todo',
        backref='list',
        cascade="all, delete-orphan",
        lazy=True
    )


@app.route('/todos/create', methods=['POST'])
def create_todo():
    """The route handler for handling post request from users submitting the
    form to create a new todo item

    Returns:
        Redirect back to the list's page
    """

    error = False

    try:
        description = request.form.get('description')
        list_id = request.form.get('list_id')
        todo = Todo(description=description, list_id=list_id)
        db.session.add(todo)
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return redirect(url_for('get_list', list_id=list_id))


@app.route('/todos/<todo_id>/edit', methods=['POST'])
def set_completed_todo(todo_id):
    """The route handler for handling post request from users checking or
    unchecking a todo item

    Args:
        todo_id: A str representing the id of the todo item that was completed

    Returns:
        Response: A json object signalling the update request was successful
    """

    error = False

    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
        response = {'success': True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return jsonify(response)


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """The route handler for handling a delete request from users clicking
    the x butten next to the todo item

    Args:
        todo_id: A str representing the id of the todo item to be deleted

    Returns:
        Response: A json object signalling the deletion request was successful
    """

    error = False

    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
        response = {'success': True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return jsonify(response)


@app.route('/lists/create', methods=['POST'])
def create_list():
    """The route handler responsible to creating a list

    Returns:
        A redirect to the newly created list's page
    """

    error = False

    try:
        name = request.form.get('name')
        todo_list = TodoList(name=name)
        db.session.add(todo_list)
        db.session.commit()
        list_id = todo_list.id
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return redirect(url_for('get_list', list_id=list_id))


@app.route('/lists/<list_id>/edit', methods=['POST'])
def set_completed_list(list_id):
    """The route handler for handling post request from users clicking complete
    all todos on a list

    Args:
        list_id: A str representing the id of the todo list item where all
            todos are to be marked as complete

    Returns:
        Response: A json object signalling the update request was successful
    """

    error = False

    try:
        todo_list = TodoList.query.get(list_id)
        for todo in todo_list.todos:
            todo.completed = True
        db.session.commit()
        response = {'success': True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return jsonify(response)


@app.route('/lists/<list_id>', methods=['DELETE'])
def delete_list(list_id):
    """The route handler for handling a delete request from users clicking
    the x butten next to the todo list

    Args:
        todo_id: A str representing the id of the todo list to be deleted

    Returns:
        Response: A json object signalling the deletion request was successful
    """

    error = False

    try:
        todo_list = TodoList.query.get(list_id)
        db.session.delete(todo_list)
        db.session.commit()
        response = {'success': True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return jsonify(response)


@app.route('/lists/<list_id>')
def get_list(list_id):
    """The route handler for a list's page

    Args:
        list_id: A str representing the id of the list to navigate to

    Returns:
        A template representing the page for a given list
    """
    lists = TodoList.query.all()
    active_list = TodoList.query.get(list_id)
    todos = Todo.query.filter_by(list_id=list_id).order_by('id').all()
    return render_template(
        'index.html',
        lists=lists,
        active_list=active_list,
        todos=todos
    )


@app.route('/')
def index():
    """The route handler for the homepage

    Returns:
        A redirect to the first list in the db
    """
    first_list = TodoList.query.first()
    return redirect(url_for('get_list', list_id=first_list.id))


if __name__ == '__main__':
    app.run(debug=True)
