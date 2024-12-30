from db import db

class BoardModel(db.Model):
    __tablename__ = 'board'

    id = db.Column(db.String(4), primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=False)

    threads = db.relationship('ThreadModel', back_populates='board', lazy='dynamic', cascade='all, delete')
