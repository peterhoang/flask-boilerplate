# Flask Minimum Boilerplate App

Flask Minimum Boilerplate is a minimal boilerplate for prototyping a backend appliation with Flask and python.

Features [Flask-RESTX](https://github.com/python-restx/flask-restx) for [Swagger](https://swagger.io/) support; [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/en/stable/) for JSON Web Token support; pytest and coverage for testing

This project is for educational purposes.

## Compatibility

Requires [Python 3.9+.](https://www.python.org/)

## Dependencies

- [Flask-RESTX](https://github.com/python-restx/flask-restx)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/en/stable/)
- pytest
- coverage

## Quickstart (Windows)

Run python in virtual environemnt

```console
py -3 -m venv venv
venv\Scripts\activate
```

Install the dependencies via pip

```console
pip install flask-restx flask-jwt-extended pytest coverage
```

Set the environment variables

```console
$env:FLASK_APP='myapp'
$env:FLASK_ENV='development'
$env:PYTHONPATH='<PATH\TO\THIS\BOILERPLATE>'
```

Initialize the sqllite3 database

```console
flask init-db
```

Run the app

```console
flask run
```

Unit tests and coverage

```console
pytest
coverage run -m pytest
coverage report
coverage html
```
