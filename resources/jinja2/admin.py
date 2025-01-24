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
    
    # Render the template and pass the board_groups data
    return render_template('index.html', board_groups=board_groups, threads=threads, replies=replies, boards=boards, images=images, api_key=api_key)

@blp.route('/board/<string:id>')
class Board(MethodView):
    def get(self, id):

        validate_api_key()

        board = BoardModel.query.get_or_404(id)
        boards = BoardModel.query.all()

        page = request.args.get('page', 1, type=int)
        normal_threads = ThreadModel.query.filter_by(type=0, board_id=id).order_by(ThreadModel.id.desc()).paginate(page=page, per_page=20, error_out=False)
        
        admin_threads = ThreadModel.query.filter_by(type=1, board_id=id)

        api_key = request.args.get('api_key', '')

        return render_template('board.html', board=board, boards=boards, normal_threads=normal_threads, admin_threads=admin_threads, page=page, api_key=api_key)
    
@blp.route('/thread/<string:id>')
class Thread(MethodView):
    def get(self, id):

        validate_api_key()

        thread = ThreadModel.query.get_or_404(id)
        boards = BoardModel.query.all()
        image = ImageModel.query.filter_by(thread_id=id).first()

        api_key = request.args.get('api_key', '')
        
        return render_template('thread.html', thread=thread, boards=boards, image=image, api_key=api_key)