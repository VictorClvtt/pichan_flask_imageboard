from marshmallow import Schema, fields

class PlainBoardSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)

class PlainThreadSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.String(required=True)
    content = fields.String(required=True)
    type = fields.Integer(required=True)
    user_token = fields.String(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)

class PlainReplySchema(Schema):
    id = fields.Int(dump_only=True)
    content = fields.String(required=True)
    user_token = fields.String(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)

class BoardSchema(PlainBoardSchema):
    threads = fields.List(fields.Nested(PlainThreadSchema()), dump_only=True)

class ThreadSchema(PlainThreadSchema):
    board_id = fields.String(required=True, load_only=True)
    board = fields.Nested(PlainBoardSchema(), dump_only=True)
    replies = fields.List(fields.Nested(PlainReplySchema()), dump_only=True)

class ReplySchema(PlainReplySchema):
    thread_id = fields.String(required=True, load_only=True)
    thread = fields.Nested(PlainThreadSchema(), dump_only=True)