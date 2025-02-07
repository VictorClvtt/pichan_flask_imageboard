from db import db
import base64

class ReplyModel(db.Model):
    __tablename__ = 'reply'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(310), unique=False, nullable=False)
    type = db.Column(db.Integer, unique=False, nullable=False)
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

    def serialize(self):
        """Converts the ReplyModel instance into a serializable dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type,
            "user_token": self.user_token,
            "date": self.date.isoformat() if self.date else None,
            "time": self.time.strftime("%H:%M:%S") if self.time else None,
            "thread_id": self.thread_id,
            "reply_id": self.reply_id,
            "image": base64.b64encode(self.image.image).decode("utf-8") if self.image and self.image.image else None,
            "votes_count": self.votes.count(),
            "replies": [reply.serialize() for reply in self.reply_replies]  # Recursive serialization for replies
        }

