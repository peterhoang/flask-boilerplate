import sqlite3, datetime, click, random
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


@click.command("inject-dummy-data")
@with_appcontext
def inject_dummy_data():
    """Injecting some dummy data"""
    db = get_db()

    db.execute("Insert Into user (username, password) values (?, ?)", ("test", generate_password_hash("test")))

    for i in range(100):
        title = f"test title {i}"
        body = f"test body body body {i}"
        created = datetime.datetime(2021, (i % 11) + 1, random.randrange(1, 28))
        db.execute("Insert Into post (title, body, author_id, created) values (?, ?, ?, ?)", (title, body, 1, created))
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(inject_dummy_data)
