"""A todo app built in flask with a postgresql db.

Usage: flask run

Attributes:
    DIALECT: A str representing the dialect of the db
    HOST: A str representing the host of the db
    PORT: An int representing the port the db is running on
    DATABASE: A str representing the db in which to connect to
    app: A flask Flask object creating the flask app
    SQLALCHEMY_DATABASE_URI: A str representing the location of the db
    db: A SQLAlchemy service
    migrate: A flask_migrate Migrate object bound to app and db

Classes:
    Todo()
    TodoList()
"""

import sys

from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

DIALECT = "postgresql"
HOST = "localhost"
PORT = 5432
DATABASE = "todo_app"

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = f"{DIALECT}://{HOST}:{PORT}/{DATABASE}"
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todo(db.Model):
    """A model representing a todo item.

    Attributes:
        id: A unique identifier for a todo object
        description: A str representing the todo object's content
        list_id: A foreign key linking a todo item to a todo list
    """

    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(
        db.Integer, db.ForeignKey("todo_lists.id"), nullable=False
    )

    def __repr__(self):
        """A Todo object's str representation."""
        return f"<Todo {self.id} {self.description}>"


class TodoList(db.Model):
    """A model representing a todo list.

    Attributes:
        id: A unique identifier for a todo list object
        name: A str representing the todo list object's name
        todos: A relationship for a foreign key on the todo item model
    """

    __tablename__ = "todo_lists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship(
        "Todo", backref="list", cascade="all, delete-orphan", lazy=True
    )


@app.route("/todos/create", methods=["POST"])
def create_todo():
    """The route handler for creating a new todo item.

    Returns:
        Redirect back to the list's page
    """
    error = False

    try:
        description = request.form.get("description")
        list_id = request.form.get("list_id")
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

    return redirect(url_for("get_list", list_id=list_id))


@app.route("/todos/<todo_id>/edit", methods=["POST"])
def set_completed_todo(todo_id):
    """The route handler setting a todo item to completed.

    Args:
        todo_id: A str representing the id of the todo item that was completed

    Returns:
        Response: A json object signalling the update request was successful
    """
    error = False

    try:
        completed = request.get_json()["completed"]
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
        response = {"success": True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return jsonify(response)


@app.route("/todos/<todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """The route handler for deleting a todo item.

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
        response = {"success": True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return jsonify(response)


@app.route("/lists/create", methods=["POST"])
def create_list():
    """The route handler responsible to creating a list.

    Returns:
        A redirect to the newly created list's page
    """
    error = False

    try:
        name = request.form.get("name")
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

    return redirect(url_for("get_list", list_id=list_id))


@app.route("/lists/<list_id>/edit", methods=["POST"])
def set_completed_list(list_id):
    """The route handler for marking all todo items in a list as competed.

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
        response = {"success": True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return jsonify(response)


@app.route("/lists/<list_id>", methods=["DELETE"])
def delete_list(list_id):
    """The route handler for deleting a list.

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
        response = {"success": True}
    except Exception:  # pylint: disable=broad-except
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(500)

    return jsonify(response)


@app.route("/lists/<list_id>")
def get_list(list_id):
    """The route handler for a list's page.

    Args:
        list_id: A str representing the id of the list to navigate to

    Returns:
        A template representing the page for a given list
    """
    lists = TodoList.query.all()
    active_list = TodoList.query.get(list_id)
    todos = Todo.query.filter_by(list_id=list_id).order_by("id").all()

    return render_template(
        "index.html", lists=lists, active_list=active_list, todos=todos
    )


@app.route("/")
def index():
    """The route handler for the homepage.

    Returns:
        A redirect to the first list in the db
    """
    first_list = TodoList.query.first()
    return redirect(url_for("get_list", list_id=first_list.id))


if __name__ == "__main__":
    app.run(debug=True)
