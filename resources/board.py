from flask import request
from flask.views import MethodView
from flask import render_template
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.board_group import BoardGroupModel
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
import re
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

    formatted_content = '<br>'.join(formatted_lines)

    # Handle spoilers (text wrapped in ::spoiler::)
    formatted_content = re.sub(r'::(.*?)::', r'<span class="spoiler">\1</span>', formatted_content)

    return formatted_content

def format_reply_content(reply):
    """Recursively format reply content and its nested replies."""
    if isinstance(reply, dict):
        reply['content'] = format_text(reply['content'])
        if 'reply_replies' in reply and reply['reply_replies']:
            for nested_reply in reply['reply_replies']:
                format_reply_content(nested_reply)
    else:
        reply.content = format_text(reply.content)
        if hasattr(reply, 'reply_replies') and reply.reply_replies:
            for nested_reply in reply.reply_replies:
                format_reply_content(nested_reply)

def reply_list(thread, replies, level=0):
    # Initialize reply_list if it doesn't exist
    if not hasattr(thread, 'reply_list'):
        thread.reply_list = []

    for reply in replies:
        # Append each reply along with its level to the thread's reply_list
        thread.reply_list.append({
            **vars(reply),
            'reply': reply.reply,
            'related_thread_id': thread.id,
            'image': reply.image,
            'level': level
        })
        
        # If the reply has nested replies, recurse into them
        if hasattr(reply, 'reply_replies') and reply.reply_replies:
            reply_list(thread, reply.reply_replies, level + 1)


@blp.route('/board/<string:id>')
class Board(MethodView):

    def get(self, id):

        board_groups = BoardGroupModel.query.all()
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

        for thread in normal_threads:
            reply_list(thread, thread.replies)
            
        # Query for admin threads
        admin_threads = ThreadModel.query.filter_by(type=1, board_id=id).order_by(ThreadModel.id.desc())
        admin_threads = admin_threads[:3]

        for thread in admin_threads:
            reply_list(thread, thread.replies)

        # Format content for normal threads
        for thread in normal_threads.items:
            thread.content = format_text(thread.content)  # Apply formatting to the thread's content
            # Format replies content recursively
            for reply in thread.reply_list:
                format_reply_content(reply)

        # Format content for admin threads
        for thread in admin_threads:
            thread.content = format_text(thread.content)  # Apply formatting to the thread's content
            # Format replies content recursively
            for reply in thread.reply_list:
                format_reply_content(reply)

        # Sorting and ordering parameters
        sort = request.args.get('sort')
        order = request.args.get('order')

        # Render the board page with formatted threads
        return render_template(
            'board.html',
            board_groups=board_groups,
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