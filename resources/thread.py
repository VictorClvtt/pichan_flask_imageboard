from flask import request, jsonify
from flask.views import MethodView
from flask import render_template, redirect
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.thread import ThreadModel
from models.image import ImageModel
from models.board_group import BoardGroupModel
from marshmallow_schemas import ThreadSchema, PlainThreadSchema


blp = Blueprint('Threads', __name__, description='Operations on threads')


API_KEYS = {"senha", "password"}

def validate_api_key():
    api_key = request.args.get('api_key')  # Get the API key from the query string
    if api_key not in API_KEYS:
        abort(403, message="Invalid or missing API key.")



from datetime import datetime, timezone

@blp.route('/thread')
class ThreadList(MethodView):

    @blp.response(200, ThreadSchema(many=True))
    def get(self):
        return ThreadModel.query.all()
    
    @blp.response(201, ThreadSchema)
    def post(self):
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        thread_type = request.form.get('type', 0)  # Default to 0
        user_token = request.form.get('user_token')
        board_id = request.form.get('board_id')

        # Get image file
        image_file = request.files.get('image')
        image_name = request.form.get('image_name')  # Image metadata
        measures = request.form.get('image_width') + 'x' + request.form.get('image_height')
        size = request.form.get('image_size')

        # Validate inputs
        if not title or not content or not user_token or not board_id or not image_file:
            return jsonify({"error": {"All fields are required."}}), 400

        current_datetime = datetime.now()

        # Extract the current date and time
        current_date = current_datetime.date()
        current_time = current_time = current_datetime.replace(microsecond=0).time()

        # Start transaction
        try:
            # Create new thread
            new_thread = ThreadModel(
                title=title,
                content=content,
                type=int(thread_type),
                user_token=user_token,
                date=current_date,
                time=current_time,
                board_id=board_id
            )

            db.session.add(new_thread)
            db.session.flush()  # Ensure thread ID is generated

            # Create new image and link to thread
            new_image = ImageModel(
                name=image_name or image_file.filename,  # Default to filename
                measures=measures,
                size=size,
                image=image_file.read(),
                thread_id=new_thread.id,
                reply_id=None
            )

            db.session.add(new_image)
            db.session.commit()

            return redirect(f'/board/{new_thread.board.id}#t{new_thread.id}')

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


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
            'related_thread_id': thread.id,
            'image': reply.image,
            'level': level
        })
        
        # If the reply has nested replies, recurse into them
        if hasattr(reply, 'reply_replies') and reply.reply_replies:
            reply_list(thread, reply.reply_replies, level + 1)

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
    
@blp.route('/thread_data/<string:id>')
class Thread(MethodView):

    @blp.response(200, ThreadSchema)
    def get(self, id):
        thread = ThreadModel.query.get_or_404(id)
        image = ImageModel.query.filter_by(thread_id=id).first()

        # Format thread content
        thread.content = format_text(thread.content)

        # Add image details to the response
        return {
            "id": thread.id,
            "title": thread.title,
            "content": thread.content,
            "user_token": thread.user_token,
            "type": thread.type,
            "date": thread.date,
            "time": thread.time,
            "image": {
                "id": image.id
                }
        }
