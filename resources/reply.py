from flask import request, jsonify, url_for
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.reply import ReplyModel
from models.thread import ThreadModel
from models.image import ImageModel
from marshmallow_schemas import ReplySchema, PlainReplySchema


blp = Blueprint('Replies', __name__, description='Operations on replies')


API_KEYS = {"cu", "valid_api_key_2"}

def validate_api_key():
    api_key = request.args.get('api_key')  # Get the API key from the query string
    if api_key not in API_KEYS:
        abort(403, message="Invalid or missing API key.")


@blp.route('/reply')
class ReplyList(MethodView):

    @blp.response(200, ReplySchema(many=True))
    def get(self):
        return ReplyModel.query.all()
    
    @blp.arguments(ReplySchema)
    @blp.response(201, ReplySchema)
    def post(self, req_data):

        thread = ThreadModel.query.get(req_data['thread_id'])
        reply = ReplyModel.query.get(req_data['reply_id'])
        if not thread and not reply:
            abort(400, message='Invalid thread or reply ID.')

        new_reply = ReplyModel(**req_data)

        # Inserting new Thread
        try:
            db.session.add(new_reply)
            db.session.commit() 
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting the data.')  

        return new_reply, 201

@blp.route('/reply/<string:id>')
class Reply(MethodView):

    @blp.response(200, ReplySchema)
    def get(self, id):
        # Fetch the reply
        reply = ReplyModel.query.get_or_404(id)

        reply = {
            "content": reply.content,
            "date": reply.date,
            "id": reply.id,
            "time": reply.time,
            "type": reply.type,
            "user_token": reply.user_token,
            "image": {
                "id": reply.image.id
            }
        }

        
        return reply


    def delete(self, id):

        validate_api_key()

        reply = ReplyModel.query.get_or_404(id)

        db.session.delete(reply)
        db.session.commit()

        return {'message': f'Reply {id} deleted.'}

import html
import bleach
import re
from bleach.linkifier import Linker

def format_text(content):
    if not content:
        return content

    # Clean the content with bleach after escaping it
    content = bleach.clean(content, tags=['span', 'br', 'a'], attributes={'span': ['class'], 'a': ['href']}, strip=True)

    linker = Linker()
    content = linker.linkify(content)

    # Format lines starting with '>' and '<'
    formatted_lines = []
    for line in content.split('\n'):
        if line.startswith('&gt;'):  # Escaped '>'
            formatted_lines.append(f"<span class='green-text'>{line}</span>")
        elif line.startswith('&lt;'):  # Escaped '<'
            formatted_lines.append(f"<span class='red-text'>{line}</span>")
        else:
            formatted_lines.append(line)

    formatted_content = '<br>'.join(formatted_lines)

    # Handle spoilers (text wrapped in ::spoiler::)
    formatted_content = re.sub(r'::(.*?)::', r'<span class="spoiler">\1</span>', formatted_content)

    return formatted_content


def format_reply_content(reply):
    """Recursively format reply content and its nested replies."""
    if isinstance(reply, dict):
        # Check if the dictionary has content and format it
        if 'content' in reply:
            reply['content'] = format_text(reply['content'])
        
        # Format nested replies
        if 'reply_replies' in reply and reply['reply_replies']:
            for nested_reply in reply['reply_replies']:
                format_reply_content(nested_reply)
    else:
        # For objects, make sure the content is being handled correctly
        reply.content = format_text(reply.content)
        
        # Format nested replies
        if hasattr(reply, 'reply_replies') and reply.reply_replies:
            for nested_reply in reply.reply_replies:
                format_reply_content(nested_reply)


def serialize_reply(reply, thread_id, level=0):
    """Recursively serialize a reply and its nested replies."""
    return {
        "id": reply.id,
        "content": format_text(reply.content),
        "type": reply.type,
        "user_token": reply.user_token,
        "date": reply.date.isoformat() if reply.date else None,
        "time": reply.time.strftime("%H:%M:%S") if reply.time else None,
        "thread_id": thread_id,
        "reply_id": reply.reply_id,
        "reply": {
            "id": reply.reply.id if reply.reply else None,
            "user_token": reply.reply.user_token if reply.reply else None,
            "date": reply.reply.date.isoformat() if reply.reply and reply.reply.date else None,
            "time": reply.reply.time.strftime("%H:%M:%S") if reply.reply and reply.reply.time else None,
            "content": reply.reply.content if reply.reply else None,
            "image": {
                "id": reply.reply.image.id if reply.reply and reply.reply.image else None,
                "name": reply.reply.image.name if reply.reply and reply.reply.image else None,
                "size": reply.reply.image.size if reply.reply and reply.reply.image else None,
                "measures": reply.reply.image.measures if reply.reply and reply.reply.image else None
            } if reply.reply and reply.reply.image else None
        } if reply.reply else None,
        "image": {
            "id": reply.image.id if reply.image else None,
            "name": reply.image.name if reply.image else None,
            "size": reply.image.size if reply.image else None,
            "measures": reply.image.measures if reply.image else None
        } if reply.image else None,
        "votes": reply.votes.count() if reply.votes else 0,  # Ensure safe handling of votes
        "level": level,
        "reply_replies": [serialize_reply(nested_reply, thread_id, level + 1) for nested_reply in reply.reply_replies]
    }


def flatten_replies(replies, thread_id, level=0):
    """Converts a list of replies and nested replies into a flat list."""
    flat_list = []

    for reply in replies:
        serialized_reply = serialize_reply(reply, thread_id, level)
        flat_list.append(serialized_reply)

        if reply.reply_replies:
            flat_list.extend(flatten_replies(reply.reply_replies, thread_id, level + 1))

    return flat_list

@blp.route('/replies/<int:thread_id>')
class RepliesByThread(MethodView):
    def get(self, thread_id):
        replies = ReplyModel.query.filter_by(thread_id=thread_id).all()

        # Format main replies (before processing nested ones)
        for reply in replies:
            reply.content = format_text(reply.content)

        # Format nested replies (ensures all levels are formatted)
        for reply in replies:
            format_reply_content(reply)

        # Convert replies and nested replies into a flat list
        return jsonify(flatten_replies(replies, thread_id))

