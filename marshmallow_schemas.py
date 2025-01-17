from marshmallow import Schema, fields

class PlainBoardSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)

class PlainThreadSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.String(required=True)
    content = fields.String(required=True)
    type = fields.Integer(required=False)
    user_token = fields.String(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)

class PlainReplySchema(Schema):
    id = fields.Int(dump_only=True)
    content = fields.String(required=True)
    user_token = fields.String(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)

class PlainBoardGroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)

class BoardSchema(PlainBoardSchema):
    threads = fields.List(fields.Nested(PlainThreadSchema()), dump_only=True)
    board_group_id = fields.Integer(required=True, load_only=True)
    board_group = fields.Nested(PlainBoardGroupSchema(), dump_only=True)

class ThreadSchema(PlainThreadSchema):
    board_id = fields.String(required=True, load_only=True)
    board = fields.Nested(PlainBoardSchema(), dump_only=True)
    replies = fields.List(fields.Nested('ReplySchema'), dump_only=True)

class ReplySchema(PlainReplySchema):
    thread_id = fields.String(required=True, load_only=True)
    thread = fields.Nested(PlainThreadSchema(), dump_only=True)

    reply_id = fields.String(required=True, load_only=True)
    reply = fields.Nested(PlainReplySchema(), dump_only=True)
    reply_replies = fields.List(fields.Nested("ReplySchema"), dump_only=True)

class BoardGroupSchema(PlainBoardGroupSchema):
    boards = fields.List(fields.Nested(PlainBoardSchema()), dump_only=True)