from db import db

class ReplyModel(db.Model):
    __tablename__ = 'reply'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(310), unique=False, nullable=False)
    user_token = db.Column(db.String(64), unique=False, nullable=False)
    date = db.Column(db.Date, unique=False, nullable=False)
    time = db.Column(db.Time, unique=False, nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), unique=False, nullable=False)

    thread = db.relationship('ThreadModel', back_populates='replies')