from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from .base import Base

class TrackedConversions(Base):
    __tablename__ = "tracked_conversions"
    id = Column('id', Integer, primary_key=True)
    from_currency_id = Column(Integer, ForeignKey('currencies.id', name='from_currency_id'), nullable=False)
    to_currency_id = Column(Integer, ForeignKey('currencies.id', name='to_currency_id'), nullable=False)
