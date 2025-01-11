from db import db

class ThreadModel(db.Model):
    __tablename__ = 'thread'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), unique=False, nullable=False)
    content = db.Column(db.String(310), unique=False, nullable=False)
    type = db.Column(db.Integer, unique=False, nullable=False)
    user_token = db.Column(db.String(64), unique=False, nullable=False)
    date = db.Column(db.Date, unique=False, nullable=False)
    time = db.Column(db.Time, unique=False, nullable=False)
    board_id = db.Column(db.String(4), db.ForeignKey('board.id'), unique=False, nullable=False)

    board = db.relationship('BoardModel', back_populates='threads')

    replies = db.relationship('ReplyModel', back_populates='thread', lazy='dynamic', cascade='all, delete')
