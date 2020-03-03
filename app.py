"""A todo app built in flask with a postgresql db"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    """The route handler for the homepage

    Returns:
        A template representing the homepage
    """
    data = [
        {'description': 'Todo 1'},
        {'description': 'Todo 2'},
        {'description': 'Todo 3'},
    ]
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
