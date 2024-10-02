from sqlalchemy import Column, Integer, String
from .base import Base

class Currencies(Base):
    __tablename__ = "currencies"
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
