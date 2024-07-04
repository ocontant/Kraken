# krakenfx/api/models/tradeBalanceModel.py
from sqlalchemy import Column, String, Integer, Float
from krakenfx.api.models import Base

class ModelTradeBalance(Base):
    __tablename__ = 'trade_balance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Float, nullable=False)  # Timestamp as float
    eb = Column(String, nullable=False)  # Equivalent balance (combined balance of all currencies)
    tb = Column(String, nullable=False)  # Trade balance (combined balance of all equity currencies)
    m = Column(String, nullable=False)  # Margin amount of open positions
    n = Column(String, nullable=False)  # Unrealized net profit/loss of open positions
    c = Column(String, nullable=False)  # Cost basis of open positions
    v = Column(String, nullable=False)  # Current floating valuation of open positions
    e = Column(String, nullable=False)  # Equity
    mf = Column(String, nullable=False)  # Free margin
    ml = Column(String, nullable=False)  # Margin level
    
