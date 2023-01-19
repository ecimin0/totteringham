import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.sql import select
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='should_definitely_not_be_in_git',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_DATABASE_URI=os.environ.get("AWS_DB_URI")
    )

    db.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import main
    app.register_blueprint(main.bp)

    return app