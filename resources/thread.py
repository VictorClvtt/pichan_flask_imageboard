from flask import request
from flask.views import MethodView
from flask import render_template
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.thread import ThreadModel
from models.board_group import BoardGroupModel
from models.image import ImageModel
from marshmallow_schemas import ThreadSchema


blp = Blueprint('Threads', __name__, description='Operations on threads')


API_KEYS = {"cu", "valid_api_key_2"}

def validate_api_key():
    api_key = request.args.get('api_key')  # Get the API key from the query string
    if api_key not in API_KEYS:
        abort(403, message="Invalid or missing API key.")


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

def format_reply_content(reply):
    """Recursively format reply content and its nested replies."""
    reply.content = format_text(reply.content)
    if hasattr(reply, 'reply_replies') and reply.reply_replies:
        for nested_reply in reply.reply_replies:
            format_reply_content(nested_reply)


@blp.route('/thread/<string:id>')
class Thread(MethodView):

    def get(self, id):

        board_groups = BoardGroupModel.query.all()
        # Get the thread, board, and image data
        thread = ThreadModel.query.get_or_404(id)

        image = ImageModel.query.filter_by(thread_id=id).first()

        # Format thread content
        thread.content = format_text(thread.content)

        # Format replies content recursively
        for reply in thread.replies:
            format_reply_content(reply)

        # Return the rendered template with the formatted content
        return render_template('thread.html', thread=thread, board_groups=board_groups, image=image)



    def delete(self, id):

        validate_api_key()

        thread = ThreadModel.query.get_or_404(id)

        db.session.delete(thread)
        db.session.commit()

        return {'message': f'Thread {id} deleted.'}