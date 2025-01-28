from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask.views import MethodView

from flask import render_template
from flask_smorest import Blueprint
from models.board_group import BoardGroupModel
from models.board import BoardModel
from models.thread import ThreadModel
from models.reply import ReplyModel
from models.image import ImageModel

from datetime import datetime


# Define a Flask-Smorest Blueprint
blp = Blueprint("Admin", __name__, url_prefix="/admin")


API_KEYS = {"cu", "valid_api_key_2"}

def validate_api_key():
    api_key = request.args.get('api_key')  # Get the API key from the query string
    if api_key not in API_KEYS:
        abort(403, message="Invalid or missing API key.")

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


@blp.route('/')
@blp.alt_response(403, description="Access denied")
def home():

    validate_api_key()

    board_groups = BoardGroupModel.query.all()
    threads = ThreadModel.query.all()
    replies = ReplyModel.query.all()

    boards = BoardModel.query.all()
    

    images = ImageModel.query.all()
    images = [
        {
            "id": image.id,
            "name": image.name,
            "measures": image.measures,
            "size": int(image.size),
            "thread_id": image.thread_id,
            "reply_id": image.reply_id,
        }
        for image in images
    ]

    api_key = request.args.get('api_key', '')

    board_stats = []
    for board in boards:
        # Total threads and replies
        total_threads = board.threads.count()
        total_replies = sum(thread.replies.count() for thread in board.threads)

        # Sum of image sizes (thread + reply images)
        total_image_size = sum(
            int(image.size) for thread in board.threads
            for image in [thread.image] if image
        ) + sum(
            int(image.size) for thread in board.threads
            for reply in thread.replies for image in [reply.image] if image
        )

        # Calculate total votes for threads and replies
        total_votes = sum(thread.votes.count() for thread in board.threads) + sum(
            reply.votes.count() for thread in board.threads for reply in thread.replies
        )

        # Calculate time range for mean posts and votes per hour/day
        now = datetime.utcnow()
        first_thread = board.threads.order_by(ThreadModel.date.asc(), ThreadModel.time.asc()).first()
        if first_thread:
            first_thread_datetime = datetime.combine(first_thread.date, first_thread.time)
            hours_diff = max((now - first_thread_datetime).total_seconds() / 3600, 1)
            days_diff = max(hours_diff / 24, 1)
        else:
            hours_diff = 1
            days_diff = 1

        # Mean posts per hour and per day
        mean_posts_per_hour = (total_threads + total_replies) / hours_diff
        mean_posts_per_day = (total_threads + total_replies) / days_diff

        # Mean votes per hour and per day
        mean_votes_per_hour = total_votes / hours_diff
        mean_votes_per_day = total_votes / days_diff

        board_stats.append({
            "id": board.id,
            "name": board.name,
            "description": board.description,
            "total_threads": total_threads,
            "total_replies": total_replies,
            "total_image_size": total_image_size,
            "total_votes": total_votes,
            "mean_posts_per_hour": round(mean_posts_per_hour, 1),
            "mean_posts_per_day": round(mean_posts_per_day, 1),
            "mean_votes_per_hour": round(mean_votes_per_hour, 1),
            "mean_votes_per_day": round(mean_votes_per_day, 1),
        })
    
    # Render the template and pass the board_groups data
    return render_template('index.html', board_groups=board_groups, threads=threads, replies=replies, boards=boards, images=images, board_stats=board_stats, api_key=api_key)

@blp.route('/board/<string:id>')
class Board(MethodView):
    def get(self, id):

        validate_api_key()

        board = BoardModel.query.get_or_404(id)
        boards = BoardModel.query.all()

        page = request.args.get('page', 1, type=int)
        normal_threads = ThreadModel.query.filter_by(type=0, board_id=id).order_by(ThreadModel.id.desc()).paginate(page=page, per_page=20, error_out=False)
        
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

        api_key = request.args.get('api_key', '')

        return render_template('board.html', board=board, boards=boards, normal_threads=normal_threads, admin_threads=admin_threads, page=page, api_key=api_key)
    
@blp.route('/thread/<string:id>')
class Thread(MethodView):
    def get(self, id):

        validate_api_key()

        thread = ThreadModel.query.get_or_404(id)
        boards = BoardModel.query.all()
        image = ImageModel.query.filter_by(thread_id=id).first()

        # Format thread content
        thread.content = format_text(thread.content)

        # Format replies content
        for reply in thread.replies:
            reply.content = format_text(reply.content)

        api_key = request.args.get('api_key', '')
        
        return render_template('thread.html', thread=thread, boards=boards, image=image, api_key=api_key)