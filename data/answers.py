import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase


class Answers(SqlAlchemyBase):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    question_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=False, autoincrement=True)
    user = orm.relationship('User')