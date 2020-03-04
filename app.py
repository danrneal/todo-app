"""A todo app built in flask with a postgresql db"""

import sys
from flask import Flask, render_template, request, jsonify, abort
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

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


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
    except Exception:
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
    data = Todo.query.all()
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
