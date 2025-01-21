from db import db

class VoteModel(db.Model):
    __tablename__ = 'vote'

    id = db.Column(db.Integer, primary_key=True)
    up_or_down = db.Column(db.Integer, unique=False, nullable=False)
    user_token = db.Column(db.String(64), unique=False, nullable=False)
    date = db.Column(db.Date, unique=False, nullable=False)
    time = db.Column(db.Time, unique=False, nullable=False)
    
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), unique=False, nullable=True)
    reply_id = db.Column(db.Integer, db.ForeignKey('reply.id'), unique=False, nullable=True)

    thread = db.relationship('ThreadModel', back_populates='votes')
    reply = db.relationship('ReplyModel', back_populates='votes')

    

