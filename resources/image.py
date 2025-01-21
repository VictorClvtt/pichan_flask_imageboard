from flask import request, jsonify, Response
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.image import ImageModel
from marshmallow_schemas import ImageSchema

from datetime import date

blp = Blueprint('Images', __name__, description='Operations on images for threads and replies')


@blp.route('/image')
class ImageList(MethodView):

    @blp.response(200, ImageSchema(many=True))
    def get(self):
        images = ImageModel.query.all()  # Get all images from the database
        return images
    
    @blp.response(201, ImageSchema)
    def post(self):
        # Get the file and form data
        image_file = request.files.get('image')  # File upload
        name = request.form.get('name')         # Image name
        mimetype = request.form.get('mimetype') # MIME type
        thread_id = request.form.get('thread_id')  # Thread ID

        # Validate inputs
        if not image_file or not name or not mimetype or not thread_id:
            return jsonify({"error": "All fields are required"}), 400

        try:
            thread_id = int(thread_id)  # Ensure thread_id is an integer
        except ValueError:
            return jsonify({"error": "Thread ID must be an integer"}), 400

        try:
            # Create new image entry
            new_image = ImageModel(
                name=name,
                mimetype=mimetype,
                image=image_file.read(),  # Read binary data from the file
                thread_id=thread_id
            )

            # Insert into the database
            db.session.add(new_image)
            db.session.commit()

            # Return JSON response
            return jsonify({
                "message": "Image uploaded successfully",
                "image": {
                    "id": new_image.id,
                    "name": new_image.name,
                    "mimetype": new_image.mimetype,
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

        return Response(image.image, mimetype=image.mimetype)

    def delete(self, id):
        image = ImageModel.query.get_or_404(id)

        db.session.delete(image)
        db.session.commit()

        return {'message': f'Reply {id} deleted.'}