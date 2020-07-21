# Todo App

A todo app built in flask with a postgresql db. This app allows you to create multiple todo lists and keep track of your progress.

## Set-up

Set-up a virtual environment and activate it:

```bash
python3 -m venv env
source env/bin/activate
```

You should see (env) before your command prompt now. (You can type `deactivate` to exit the virtual environment any time.)

Install the requirements:

```bash
pip install -U pip
pip install -r requirements.txt
```

Initialize and set up the database:

```bash
dropdb todo_app
createdb todo_app
flask db upgrade
```

## Usage

Make sure you are in the virtual environment (you should see (env) before your command prompt). If not `source /env/bin/activate` to enter it.

```bash
Usage: flask run
```

## Screenshots

![Todo App](https://i.imgur.com/ctPcByu.png)

## Credit

[Udacity's Full Stack Web Developer Nanodegree Program](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044)

## License

Todo App is licensed under the [MIT license](https://github.com/danrneal/todo-app/blob/master/LICENSE).
