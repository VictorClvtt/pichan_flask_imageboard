from flask import request
from flask.views import MethodView
from flask import render_template
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.board import BoardModel
from models.thread import ThreadModel
from models.reply import ReplyModel
from models.vote import VoteModel
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

        page = request.args.get('page', 1, type=int)
        normal_threads = ThreadModel.query.filter_by(type=0, board_id=id) \
            .order_by(ThreadModel.id.desc()) \
            .paginate(page=page, per_page=20, error_out=False)

        # To get the last 500 threads in total, you can manually limit the results:
        normal_threads.items = normal_threads.items[:500]

        admin_threads = ThreadModel.query.filter_by(type=1, board_id=id).order_by(ThreadModel.id.desc())

        sort = request.args.get('sort')
        order = request.args.get('order')

        return render_template(
            'board.html',
            board=board,
            boards=boards,
            normal_threads=normal_threads, 
            admin_threads=admin_threads, 
            page=page,
            sort=sort,
            order=order
        )




    def delete(self, id):

        validate_api_key()

        board = BoardModel.query.get_or_404(id)

        db.session.delete(board)
        db.session.commit()

        return {'message': f'Board {id} deleted.'}