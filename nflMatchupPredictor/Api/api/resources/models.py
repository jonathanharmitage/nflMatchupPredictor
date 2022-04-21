from flask import request, jsonify
from flask_restful import Resource

from Api.api.schemas import TrainModelSchema, TrainModelResultSchema
from Models.CorrelationModels import CorrelationDataLoader, CorrelationModel
from Models.ModelAnalyzer import ModelAnalyzer


class ModelResource(Resource):
    """Model resource

    ---
    post:
        tags:
            - api
        summary: Train a model
        description: Trains a model
        parameters:
            - in: path
              name: model_key
              schema:
                type: string
        requestBody:
            content:
                application/json:
                    schema:
                        TrainModelSchema
        responses:
            201:
                content:
                    application/json:
                        schema:
                            TrainModelResultSchema
    """

    def post(self, model_key):
        schema = TrainModelSchema()
        train_model = schema.load(request.json)
        if model_key == "Correlation":
            cdl = CorrelationDataLoader()
            cm = CorrelationModel()

            ma = ModelAnalyzer(cm, cdl)
            result = ma.analyze(
                list(
                    range(
                        train_model["train_range"]["start"],
                        train_model["train_range"]["end"] + 1,
                    )
                ),
                list(
                    range(
                        train_model["test_range"]["start"],
                        train_model["test_range"]["end"] + 1,
                    )
                ),
            )
        if model_key == "Tensor Flow":
            pass

        schema = TrainModelResultSchema()
        return schema.load({"correct": result[0], "total": result[1]})


class ModelList(Resource):
    """Get all current models

    ---
    get:
        tags:
            - api
        summary: Get a list of users
        description: Get a list of paginated users
        responses:
            200:
              content:
                application/json:
                  schema:
                    type: array
                    items:
                        type: string
    """

    def get(self):
        return jsonify(["Correlation", "Tensor Flow"])
