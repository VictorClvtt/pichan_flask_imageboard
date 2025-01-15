from flask.views import MethodView
from flask import render_template
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.board import BoardModel
from marshmallow_schemas import PlainBoardSchema, BoardSchema

blp = Blueprint('Boards', __name__, description='Operations on boards')


@blp.route('/board')
class BoardList(MethodView):

    @blp.response(200, PlainBoardSchema(many=True))
    def get(self):
        return BoardModel.query.all()
    
    @blp.arguments(BoardSchema)
    @blp.response(201, BoardSchema)
    def post(self, req_data):
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
        # Pass the board object to the template
        return render_template('board.html', board=board)

    def delete(self, id):
        board = BoardModel.query.get_or_404(id)

        db.session.delete(board)
        db.session.commit()

        return {'message': f'Board {id} deleted.'}