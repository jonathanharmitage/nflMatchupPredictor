from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError

from Api.api.resources import ModelResource, ModelList
from Api.extensions import apispec

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)

api.add_resource(ModelResource, "/models/<string:model_key>", endpoint="model_by_key")
api.add_resource(ModelList, "/models", endpoint="models")


@blueprint.before_app_first_request
def register_views():
    apispec.spec.path(view=ModelResource, app=current_app)
    apispec.spec.path(view=ModelList, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
