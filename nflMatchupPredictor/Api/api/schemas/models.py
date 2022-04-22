from marshmallow import Schema, fields


class RangeSchema(Schema):
    start = fields.Int()
    end = fields.Int()


class TrainModelResultSchema(Schema):
    correct = fields.Int()
    total = fields.Int()


class TrainModelSchema(Schema):
    train_range = fields.Nested(RangeSchema)
    test_range = fields.Nested(RangeSchema)
