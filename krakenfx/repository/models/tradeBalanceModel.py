# krakenfx/api/models/tradeBalanceModel.py
from sqlalchemy import Column, Float, Integer, String

from krakenfx.repository.models import Base


class ModelTradeBalance(Base):
    """
    Model for the trade balance.

    Attributes:
        id: Primary key, auto-incremented.
        timestamp: Timestamp as a float.
        eb: Equivalent balance (combined balance of all currencies).
        tb: Trade balance (combined balance of all equity currencies).
        m: Margin amount of open positions.
        uv: Unrealized value of open positions.
        n: Unrealized net profit/loss of open positions.
        c: Cost basis of open positions.
        v: Current floating valuation of open positions.
        e: Equity.
        mf: Free margin.
        ml: Margin level.
    """

    __tablename__ = "trade_balance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Float, nullable=False)
    eb = Column(String, nullable=False)
    tb = Column(String, nullable=False)
    m = Column(String, nullable=False)
    uv = Column(String, nullable=True)
    n = Column(String, nullable=False)
    c = Column(String, nullable=False)
    v = Column(String, nullable=False)
    e = Column(String, nullable=False)
    mf = Column(String, nullable=False)
    ml = Column(String, nullable=True)
