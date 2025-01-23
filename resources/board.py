from flask import request
from flask.views import MethodView
from flask import render_template
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.board import BoardModel
from models.thread import ThreadModel
from marshmallow_schemas import PlainBoardSchema, BoardSchema

blp = Blueprint('Boards', __name__, description='Operations on boards')


API_KEYS = {"cu", "valid_api_key_2"}

def validate_api_key():
    api_key = request.args.get('api_key')  # Get the API key from the query string
    if api_key not in API_KEYS:
        abort(403, message="Invalid or missing API key.")


@blp.route('/board')
class BoardList(MethodView):

    @blp.response(200, BoardSchema(many=True))
    def get(self):
        return BoardModel.query.all()
    
    @blp.arguments(BoardSchema)
    @blp.response(201, BoardSchema)
    def post(self, req_data):

        validate_api_key()

        new_board = BoardModel(**req_data)

        # Inserting new Board
        try:
            db.session.add(new_board)
            db.session.commit()
        except IntegrityError:
            abort(400, message='A board with that name already exists.')  
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting the data.')  

        return new_board, 201

@blp.route('/board/<string:id>')
class Board(MethodView):

    def get(self, id):
        board = BoardModel.query.get_or_404(id)
        boards = BoardModel.query.all()

        normal_threads = ThreadModel.query.filter_by(type=0, board_id=id)
        admin_threads = ThreadModel.query.filter_by(type=1, board_id=id)

        return render_template('board.html', board=board, boards=boards, normal_threads=normal_threads, admin_threads=admin_threads)

    def delete(self, id):

        validate_api_key()

        board = BoardModel.query.get_or_404(id)

        db.session.delete(board)
        db.session.commit()

        return {'message': f'Board {id} deleted.'}