from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.reply import ReplyModel
from models.thread import ThreadModel
from marshmallow_schemas import ReplySchema

from datetime import date

blp = Blueprint('Replies', __name__, description='Operations on replies')


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
        reply = ReplyModel.query.get_or_404(id)

        db.session.delete(reply)
        db.session.commit()

        return {'message': f'Reply {id} deleted.'}