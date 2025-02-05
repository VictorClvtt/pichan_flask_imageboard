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

@blp.route('/')
@blp.alt_response(403, description="Access denied")
def home():

    validate_api_key()

    board_groups = BoardGroupModel.query.all()
    threads = ThreadModel.query.all()
    replies = ReplyModel.query.all()

    boards = BoardModel.query.all()

    import random
    popular_threads = []
    for board in boards:
        max_votes = -1
        most_voted_thread = None
        for thread in board.threads:
            # Calculate vote count for the current thread
            vote_count = thread.votes.count()
            if vote_count > max_votes or (vote_count == max_votes and thread.id < most_voted_thread.id):
                max_votes = vote_count
                most_voted_thread = thread
        if most_voted_thread:
            popular_threads.append([board, most_voted_thread])
    random.shuffle(popular_threads)

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
    return render_template('index.html', board_groups=board_groups, threads=threads, replies=replies, boards=boards, images=images, board_stats=board_stats, popular_threads=popular_threads, api_key=api_key)

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
            'level': level
        })
        
        # If the reply has nested replies, recurse into them
        if hasattr(reply, 'reply_replies') and reply.reply_replies:
            reply_list(thread, reply.reply_replies, level + 1)

@blp.route('/board/<string:id>')
class Board(MethodView):
    def get(self, id):

        validate_api_key()

        board_groups = BoardGroupModel.query.all()
        board = BoardModel.query.get_or_404(id)

        page = request.args.get('page', 1, type=int)
        normal_threads = ThreadModel.query.filter_by(type=0, board_id=id).order_by(ThreadModel.id.desc()).paginate(page=page, per_page=20, error_out=False)
        
        admin_threads = ThreadModel.query.filter_by(type=1, board_id=id).order_by(ThreadModel.id.desc())

        for thread in normal_threads:
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
            for reply in thread.replies:
                format_reply_content(reply)

        # Sorting and ordering parameters
        sort = request.args.get('sort')
        order = request.args.get('order')

        api_key = request.args.get('api_key', '')

        return render_template('board.html', board=board, board_groups=board_groups, normal_threads=normal_threads, admin_threads=admin_threads, page=page, api_key=api_key, sort=sort, order=order)
    
@blp.route('/thread/<string:id>')
class Thread(MethodView):
    def get(self, id):

        validate_api_key()

        board_groups = BoardGroupModel.query.all()
        thread = ThreadModel.query.get_or_404(id)
        boards = BoardModel.query.all()
        image = ImageModel.query.filter_by(thread_id=id).first()

        # Format thread content
        thread.content = format_text(thread.content)

        # Format replies content recursively
        for reply in thread.replies:
            format_reply_content(reply)

        api_key = request.args.get('api_key', '')
        
        return render_template('thread.html', thread=thread, boards=boards, board_groups=board_groups, image=image, api_key=api_key)