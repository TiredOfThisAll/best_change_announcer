from sqlalchemy import Column, Integer, DateTime, Float, Boolean, ForeignKey
from .base import Base

class RatesHistory(Base):
    __tablename__ = "rates_history"
    id = Column('id', Integer, primary_key=True)
    conversion_id = Column(ForeignKey('currencies.id', name='conversion_id'), nullable=False)
    rate = Column('rate', Float)
    ascending = Column('ascending', Boolean)
    date = Column('date', DateTime)
