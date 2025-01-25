from flask import render_template
from flask_smorest import Blueprint
from models.board_group import BoardGroupModel
from models.board import BoardModel
from models.thread import ThreadModel
from models.reply import ReplyModel
from models.image import ImageModel

from datetime import datetime


blp = Blueprint('Index', __name__, description='Index Homepage')


@blp.route('/')
def home():

    # Fetch other data from the database
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



    # Render the template and pass the data
    return render_template(
        'index.html',
        board_groups=board_groups,
        threads=threads,
        replies=replies,
        boards=boards,
        images=images,
        board_stats=board_stats
    )
