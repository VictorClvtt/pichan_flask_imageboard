import requests
from flask import render_template
from flask_smorest import Blueprint
from models.board_group import BoardGroupModel
from models.board import BoardModel
from models.thread import ThreadModel
from models.reply import ReplyModel
from models.image import ImageModel

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

    # Render the template and pass the data
    return render_template(
        'index.html',
        board_groups=board_groups,
        threads=threads,
        replies=replies,
        boards=boards,
        images=images
    )
