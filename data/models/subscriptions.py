from sqlalchemy import Column, Integer, ForeignKey
from .base import Base

class Subscriptions(Base):
    __tablename__ = "subscriptions"
    id = Column('id', Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id', name='user_id'))
    tracked_conversions_id = Column(ForeignKey('tracked_conversions.id', name='tracked_conversion_id'))
