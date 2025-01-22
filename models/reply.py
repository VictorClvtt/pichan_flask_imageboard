from db import db
from sqlalchemy.orm import joinedload

class ReplyModel(db.Model):
    __tablename__ = 'reply'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(310), unique=False, nullable=False)
    user_token = db.Column(db.String(64), unique=False, nullable=False)
    date = db.Column(db.Date, unique=False, nullable=False)
    time = db.Column(db.Time, unique=False, nullable=False)

    # Foreign key to thread
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), unique=False, nullable=True)
    thread = db.relationship('ThreadModel', back_populates='replies')

    # Foreign key to parent reply (self-referential relationship)
    reply_id = db.Column(db.Integer, db.ForeignKey('reply.id', ondelete='CASCADE'), unique=False, nullable=True)
    reply = db.relationship('ReplyModel', back_populates='reply_replies', remote_side=[id], lazy='joined')

    # This relationship represents replies to this reply
    reply_replies = db.relationship('ReplyModel', back_populates='reply', lazy='dynamic', cascade='all, delete')

    image = db.relationship('ImageModel', back_populates='reply', uselist=False, cascade='all, delete')

    votes = db.relationship('VoteModel', back_populates='reply', lazy='dynamic', cascade='all, delete')

