from flask import request, jsonify, Response
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models.image import ImageModel
from marshmallow_schemas import ImageSchema

blp = Blueprint('Images', __name__, description='Operations on images for threads and replies')


@blp.route('/image')
class ImageList(MethodView):

    @blp.response(200, ImageSchema(many=True))
    def get(self):
        images = ImageModel.query.all()
        return images

    @blp.response(201, ImageSchema)
    def post(self):
        image_file = request.files.get('image')
        name = request.form.get('name')
        measures = request.form.get('measures')
        size = request.form.get('size')
        thread_id = request.form.get('thread_id')
        reply_id = request.form.get('reply_id')

        # Validate inputs
        if not image_file or not name or not measures or not size or not thread_id:
            return jsonify({"error": "All fields are required"}), 400

        try:
            new_image = ImageModel(
                name=name,
                measures=measures,
                size=size,
                image=image_file.read(),
                thread_id=thread_id,
                reply_id=reply_id
            )

            db.session.add(new_image)
            db.session.commit()

            return jsonify({
                "message": "Image uploaded successfully",
                "image": {
                    "id": new_image.id,
                    "name": new_image.name,
                    "measures": new_image.measures,
                    "size": new_image.size,
                    "thread_id": new_image.thread_id
                }
            }), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


@blp.route('/image/<int:id>')
class Image(MethodView):

    @blp.response(200, ImageSchema)
    def get(self, id):
        image = ImageModel.query.get_or_404(id)
        return Response(image.image, mimetype='image/jpeg')

    def delete(self, id):
        image = ImageModel.query.get_or_404(id)
        db.session.delete(image)
        db.session.commit()
        return {'message': f'Image {id} deleted.'}, 200
