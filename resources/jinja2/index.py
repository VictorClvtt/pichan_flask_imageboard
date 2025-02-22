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

    total_image_size = sum(image["size"] for image in images)

    board_stats = []
    for board in boards:
        # Total threads and replies
        total_threads = board.threads.count()
        def count_replies(replies):
            replies = list(replies)  # Convert AppenderQuery to a list
            total = len(replies)  # Count direct replies
            for reply in replies:
                total += count_replies(reply.reply_replies)  # Recursively count nested replies
            return total

        # Calculate total replies recursively for all threads in a board
        total_replies = sum(count_replies(thread.replies) for thread in board.threads)


        def count_images_in_replies(replies):
            total_size = 0
            for reply in replies:
                # Add image size of the current reply if it has an image
                if reply.image:
                    total_size += int(reply.image.size)
                
                # Recursively count images in replies of this reply
                if reply.reply_replies:
                    total_size += count_images_in_replies(reply.reply_replies)
            
            return total_size

        # Sum of image sizes (thread + reply images)
        total_image_size = sum(
            int(image.size) for thread in board.threads
            for image in [thread.image] if image
        ) + sum(
            int(image.size) for thread in board.threads
            for reply in thread.replies for image in [reply.image] if image
        ) + sum(
            count_images_in_replies(thread.replies) for thread in board.threads
        )

        def count_votes_in_replies(replies):
            total_votes = 0
            for reply in replies:
                # Add votes count of the current reply
                total_votes += reply.votes.count()
                
                # Recursively count votes in replies of this reply
                if reply.reply_replies:
                    total_votes += count_votes_in_replies(reply.reply_replies)
            
            return total_votes

        # Sum of total votes (thread votes + reply votes)
        total_votes = sum(thread.votes.count() for thread in board.threads) + sum(
            reply.votes.count() for thread in board.threads for reply in thread.replies
        ) + sum(
            count_votes_in_replies(thread.replies) for thread in board.threads
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
        total_image_size=total_image_size,
        popular_threads=popular_threads,
        board_stats=board_stats
    )
