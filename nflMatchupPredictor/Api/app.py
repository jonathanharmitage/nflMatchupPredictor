from flask import Flask
from flask_cors import CORS

from Api import api
from Api import manage
from Api.extensions import apispec
from Api.extensions import db
from Api.extensions import migrate


def create_app(testing=False):
    """Application factory, used to create application"""
    app = Flask("Api")
    app.config.from_object("Api.config")

    CORS(app)

    if testing is True:
        app.config["TESTING"] = True

    configure_extensions(app)
    configure_cli(app)
    configure_apispec(app)
    register_blueprints(app)
    setup_status(app)

    return app


def setup_status(app):
    @app.route("/")
    def status():
        return "<p>Running!</p>"


def configure_extensions(app):
    """Configure flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)


def configure_cli(app):
    """Configure Flask 2.0's cli for easy entity management"""
    app.cli.add_command(manage.init)


def configure_apispec(app):
    """Configure APISpec for swagger support"""
    apispec.init_app(app)


def register_blueprints(app):
    """Register all blueprints for application"""
    app.register_blueprint(api.views.blueprint)
