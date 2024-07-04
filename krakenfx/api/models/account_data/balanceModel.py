# my_project/api/models/balance.py
from sqlalchemy import Column, String
from krakenfx.api.models import Base

class ModelBalance(Base):
    __tablename__ = 'balances'

    asset = Column(String, primary_key=True)
    amount = Column(String, nullable=False)
