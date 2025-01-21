from db import db

class ImageModel(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary, nullable=False)  # Remove unique constraint
    name = db.Column(db.Text, nullable=False)
    measures = db.Column(db.Text, nullable=False)
    size = db.Column(db.Text, nullable=False)

    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)

    # Back-populate the relationship
    thread = db.relationship('ThreadModel', back_populates='image')

