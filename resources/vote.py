from flask.views import MethodView
from flask import jsonify
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
        # Retrieve thread and reply from the database
        thread = ThreadModel.query.get(req_data['thread_id'])
        reply = ReplyModel.query.get(req_data['reply_id'])
        
        if not thread and not reply:
            abort(400, message='Invalid thread or reply ID.')

        # Check if the user has voted on the specific thread or reply
        existing_vote = VoteModel.query.filter_by(
            user_token=req_data['user_token'],
            thread_id=req_data.get('thread_id'),
            reply_id=req_data.get('reply_id'),
        ).first()

        if existing_vote:
            # If the vote value matches, delete the existing vote
            if existing_vote.up_or_down == req_data['up_or_down']:
                try:
                    db.session.delete(existing_vote)
                    db.session.commit()
                    return '', 204  # Return 204 No Content when the vote is deleted
                except SQLAlchemyError:
                    abort(500, message='An error occurred while deleting the vote.')

            # If the vote value is different, delete the existing vote and create a new one
            try:
                db.session.delete(existing_vote)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message='An error occurred while deleting the existing vote.')

        # Create a new vote with the updated value
        new_vote = VoteModel(**req_data)
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
    
@blp.route('/vote/token/<string:token>')
class Vote(MethodView):

    @blp.response(200, VoteSchema(many=True))
    def get(self, token):
        votes = VoteModel.query.filter_by(user_token=token).all()
        if not votes:
            return {'message': 'No votes found for the specified user token.'}, 404
        return votes , 200

    def delete(self, token):
        vote = VoteModel.query.get_or_404(id)

        db.session.delete(vote)
        db.session.commit()

        return {'message': f'Thread {id} deleted.'}