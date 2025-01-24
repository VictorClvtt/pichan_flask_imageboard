from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.reply import ReplyModel
from models.thread import ThreadModel
from marshmallow_schemas import ReplySchema


blp = Blueprint('Replies', __name__, description='Operations on replies')


API_KEYS = {"cu", "valid_api_key_2"}

def validate_api_key():
    api_key = request.args.get('api_key')  # Get the API key from the query string
    if api_key not in API_KEYS:
        abort(403, message="Invalid or missing API key.")


@blp.route('/reply')
class ReplyList(MethodView):

    @blp.response(200, ReplySchema(many=True))
    def get(self):
        return ReplyModel.query.all()
    
    @blp.arguments(ReplySchema)
    @blp.response(201, ReplySchema)
    def post(self, req_data):

        thread = ThreadModel.query.get(req_data['thread_id'])
        reply = ReplyModel.query.get(req_data['reply_id'])
        if not thread and not reply:
            abort(400, message='Invalid thread or reply ID.')

        new_reply = ReplyModel(**req_data)

        # Inserting new Thread
        try:
            db.session.add(new_reply)
            db.session.commit() 
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting the data.')  

        return new_reply, 201

@blp.route('/reply/<string:id>')
class Reply(MethodView):

    @blp.response(200, ReplySchema)
    def get(self, id):
        reply = ReplyModel.query.get_or_404(id)
        return reply

    def delete(self, id):

        validate_api_key()

        reply = ReplyModel.query.get_or_404(id)

        db.session.delete(reply)
        db.session.commit()

        return {'message': f'Reply {id} deleted.'}