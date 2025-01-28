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


import html
import bleach
from bleach.linkifier import Linker

def format_text(content):
    if not content:
        return content
    
    content = html.escape(content)
    content = bleach.clean(content, tags=['span', 'br', 'a'], attributes={'span': ['class'], 'a': ['href']}, strip=True)

    linker = Linker()
    content = linker.linkify(content)

    # Format lines starting with '>' and '<'
    formatted_lines = []
    for line in content.split('\n'):
        if line.startswith('&gt;'):  # Escaped '>'
            formatted_lines.append(f'<span class="green-text">{line}</span>')
        elif line.startswith('&lt;'):  # Escaped '<'
            formatted_lines.append(f'<span class="red-text">{line}</span>')
        else:
            formatted_lines.append(line)

    return '<br>'.join(formatted_lines)


@blp.route('/board/<string:id>')
class Board(MethodView):

    def get(self, id):
        # Get the board and all boards for navigation
        board = BoardModel.query.get_or_404(id)
        boards = BoardModel.query.all()

        # Pagination for normal threads
        page = request.args.get('page', 1, type=int)
        normal_threads = ThreadModel.query.filter_by(type=0, board_id=id) \
            .order_by(ThreadModel.id.desc()) \
            .paginate(page=page, per_page=20, error_out=False)

        # Limit the number of normal threads to 500
        normal_threads.items = normal_threads.items[:500]

        # Query for admin threads
        admin_threads = ThreadModel.query.filter_by(type=1, board_id=id).order_by(ThreadModel.id.desc())

        # Format content for normal threads
        for thread in normal_threads.items:
            thread.content = format_text(thread.content)  # Apply formatting to the thread's content
            for reply in thread.replies:  # Apply formatting to each reply's content
                reply.content = format_text(reply.content)

        # Format content for admin threads
        for thread in admin_threads:
            thread.content = format_text(thread.content)  # Apply formatting to the thread's content
            for reply in thread.replies:  # Apply formatting to each reply's content
                reply.content = format_text(reply.content)

        # Sorting and ordering parameters
        sort = request.args.get('sort')
        order = request.args.get('order')

        # Render the board page with formatted threads
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