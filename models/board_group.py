from db import db

class BoardGroupModel(db.Model):
    __tablename__ = 'board_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    boards = db.relationship('BoardModel', back_populates='board_group', lazy='dynamic', cascade='all, delete')
