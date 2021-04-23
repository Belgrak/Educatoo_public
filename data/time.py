import sqlalchemy
from .db_session import SqlAlchemyBase


class Time(SqlAlchemyBase):
    __tablename__ = 'time'

    chat_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    count = sqlalchemy.Column(sqlalchemy.Integer)