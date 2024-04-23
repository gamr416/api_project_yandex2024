'''import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Answers(SqlAlchemyBase):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    news_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("news.id"))
    news = orm.relationship("News", back_populates='user')'''