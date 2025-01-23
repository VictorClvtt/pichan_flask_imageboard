from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.board_group import BoardGroupModel
from marshmallow_schemas import PlainBoardGroupSchema, BoardGroupSchema

blp = Blueprint('Board Groups', __name__, description='Operations on board groups')


API_KEYS = {"cu", "valid_api_key_2"}

def validate_api_key():
    api_key = request.args.get('api_key')  # Get the API key from the query string
    if api_key not in API_KEYS:
        abort(403, message="Invalid or missing API key.")


@blp.route('/board_group')
class BoardGroupList(MethodView):

    @blp.response(200, BoardGroupSchema(many=True))
    def get(self):
        return BoardGroupModel.query.all()
    
    @blp.arguments(BoardGroupSchema)
    @blp.response(201, BoardGroupSchema)
    def post(self, req_data):

        validate_api_key()

        new_board_group = BoardGroupModel(**req_data)

        # Inserting new Board Group
        try:
            db.session.add(new_board_group)
            db.session.commit()
        except IntegrityError:
            abort(400, message='A board group with that name already exists.')  
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting the data.')  

        return new_board_group, 201

@blp.route('/board_group/<string:id>')
class BoardGroup(MethodView):

    @blp.response(200, BoardGroupSchema)
    def get(self, id):
        board_group = BoardGroupModel.query.get_or_404(id)
        return board_group

    def delete(self, id):
        board_group = BoardGroupModel.query.get_or_404(id)

        db.session.delete(board_group)
        db.session.commit()

        return {'message': f'Board {id} deleted.'}