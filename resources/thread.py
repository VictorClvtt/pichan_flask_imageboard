from flask.views import MethodView
from flask import render_template
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.thread import ThreadModel
from models.board import BoardModel
from models.image import ImageModel
from marshmallow_schemas import ThreadSchema

from datetime import date

blp = Blueprint('Threads', __name__, description='Operations on threads')


@blp.route('/thread')
class ThreadList(MethodView):

    @blp.response(200, ThreadSchema(many=True))
    def get(self):
        return ThreadModel.query.all()
    
    @blp.arguments(ThreadSchema)
    @blp.response(201, ThreadSchema)
    def post(self, req_data):

        board = BoardModel.query.get(req_data['board_id'])
        if not board:
            abort(400, message='Invalid board ID.')

        new_thread = ThreadModel(**req_data)

        # Inserting new Thread
        try:
            db.session.add(new_thread)
            db.session.commit() 
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting the data.')  

        return new_thread, 201

@blp.route('/thread/<string:id>')
class Thread(MethodView):

    def get(self, id):
        thread = ThreadModel.query.get_or_404(id)
        boards = BoardModel.query.all()
        image = ImageModel.query.filter_by(thread_id=id).first()
        
        return render_template('thread.html', thread=thread, boards=boards, image=image)

    def delete(self, id):
        thread = ThreadModel.query.get_or_404(id)

        db.session.delete(thread)
        db.session.commit()

        return {'message': f'Thread {id} deleted.'}