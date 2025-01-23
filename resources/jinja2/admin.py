from flask import request, jsonify
from flask_smorest import Blueprint

from flask import render_template
from flask_smorest import Blueprint
from models.board_group import BoardGroupModel
from models.board import BoardModel
from models.thread import ThreadModel
from models.reply import ReplyModel
from models.image import ImageModel

# Trusted IP addresses
TRUSTED_IPS = {"127.0.0.1"}

# Define a Flask-Smorest Blueprint
blp = Blueprint("Admin", __name__, url_prefix="/admin")

@blp.route('/')
@blp.alt_response(403, description="Access denied")
def admin_endpoint():
    """
    Endpoint accessible only to trusted IP addresses.
    """
    client_ip = request.remote_addr

    if client_ip not in TRUSTED_IPS:
        return jsonify({"error": "Access denied"}), 403

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
    
    # Render the template and pass the board_groups data
    return render_template('index.html', board_groups=board_groups, threads=threads, replies=replies, boards=boards, images=images, admin=True)