from sqlalchemy import Column, Integer, String
from .base import Base

class Users(Base):
    __tablename__ = "users"
    id = Column('id', Integer, primary_key=True)
    telegram_user_id = Column('telegram_user_id', Integer)
    username = Column('username', String)
    chat_id = Column('chat_id', Integer)
