from flask.views import MethodView
from flask import render_template
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.vote import VoteModel
from models.thread import ThreadModel
from models.reply import ReplyModel
from marshmallow_schemas import VoteSchema


blp = Blueprint('Votes', __name__, description='Operations on votes')


@blp.route('/vote')
class VoteList(MethodView):

    @blp.response(200, VoteSchema(many=True))
    def get(self):
        return VoteModel.query.all()
    
    @blp.arguments(VoteSchema)
    @blp.response(201, VoteSchema)
    def post(self, req_data):

        thread = ThreadModel.query.get(req_data['thread_id'])
        reply = ReplyModel.query.get(req_data['reply_id'])
        if not thread or not reply:
            abort(400, message='Invalid thread ID.')

        new_vote = VoteModel(**req_data)

        # Inserting new Thread
        try:
            db.session.add(new_vote)
            db.session.commit() 
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting the data.')  

        return new_vote, 201

@blp.route('/vote/<string:id>')
class Vote(MethodView):

    def get(self, id):
        vote = VoteModel.query.get_or_404(id)
        
        return vote, 200

    def delete(self, id):
        vote = VoteModel.query.get_or_404(id)

        db.session.delete(vote)
        db.session.commit()

        return {'message': f'Thread {id} deleted.'}