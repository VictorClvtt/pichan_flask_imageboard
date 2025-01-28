from flask import request
from flask.views import MethodView
from flask import render_template
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.thread import ThreadModel
from models.board import BoardModel
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

import bleach
import re
import html

def format_text(content):
    """
    Formats the content by wrapping lines starting with '>' in green text
    and lines starting with '<' in red text. It also escapes dangerous characters
    and converts URLs into clickable links.
    """
    if not content:
        return content

    # Escape '<' and '>' to prevent them from being interpreted as HTML tags
    content = html.escape(content)

    # Clean the content, allowing only specified tags and attributes
    content = bleach.clean(content, tags=['span', 'br', 'a'], attributes={'span': ['class'], 'a': ['href']}, strip=True)

    # Convert links (URLs) into clickable <a> tags
    content = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', content)

    formatted_lines = []
    for line in content.split('\n'):
        if line.startswith('&gt;'):  # Check for escaped '>' (i.e., '&gt;')
            formatted_lines.append(f'<span class="green-text">{line}</span>')
        elif line.startswith('&lt;'):  # Check for escaped '<' (i.e., '&lt;')
            formatted_lines.append(f'<span class="red-text">{line}</span>')
        else:
            formatted_lines.append(line)

    return '<br>'.join(formatted_lines)



@blp.route('/thread/<string:id>')
class Thread(MethodView):

    def get(self, id):
        # Get the thread, board, and image data
        thread = ThreadModel.query.get_or_404(id)
        boards = BoardModel.query.all()
        image = ImageModel.query.filter_by(thread_id=id).first()

        # Format thread content
        thread.content = format_text(thread.content)

        # Format replies content
        for reply in thread.replies:
            reply.content = format_text(reply.content)

        # Return the rendered template with the formatted content
        return render_template('thread.html', thread=thread, boards=boards, image=image)

    def delete(self, id):

        validate_api_key()

        thread = ThreadModel.query.get_or_404(id)

        db.session.delete(thread)
        db.session.commit()

        return {'message': f'Thread {id} deleted.'}