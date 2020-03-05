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
        description: A str representing the todo objects' content
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
    __tablename__ = 'todo_lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)


@app.route('/todos/create', methods=['POST'])
def create_todo():
    """The route handler for handling post request from users submitting the
    form to create a new todo item

    Returns:
        Response: A json object with the todo item content
    """

    error = False

    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        response = {'description': todo.description}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return jsonify(response)


@app.route('/todos/<todo_id>/edit', methods=['POST'])
def set_completed_todo(todo_id):
    """The route handler for handling post request from users checking or
    unchecking a todo item

    Returns:
        Redirects to home page
    """

    error = False

    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return redirect(url_for('index'))


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """The route handler for handling a delete request from users clicking
    the x butten next to the todo item

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


@app.route('/')
def index():
    """The route handler for the homepage

    Returns:
        A template representing the homepage
    """
    data = Todo.query.order_by('id').all()
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
