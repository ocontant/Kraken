from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from krakenfx.core.database import Base
import datetime

class ModelTradeInfo(Base):
    __tablename__ = 'trade_info'

    id = Column(String, primary_key=True, index=True, nullable=True)
    trade_id = Column(Integer, nullable=False)
    ordertxid = Column(String, ForeignKey('orders.id'), nullable=False)
    postxid = Column(String, nullable=False)
    pair = Column(String, nullable=False)
    time = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    ordertype = Column(String, nullable=False)
    price = Column(String, nullable=False)
    cost = Column(String, nullable=False)
    fee = Column(String, nullable=False)
    vol = Column(String, nullable=False)
    margin = Column(String, nullable=False)
    leverage = Column(String, nullable=True)
    misc = Column(String, nullable=True)
    maker = Column(Boolean, nullable=False)

    fk_order = relationship("ModelOrders", uselist=False)
    fk_tradeHistory = relationship("ModelTradesHistory", uselist=False, back_populates="fk_trade")

class ModelTradesHistory(Base):
    __tablename__ = 'trades_history'

    id = Column(String, primary_key=True, index=True, nullable=True)
    tradeinfo_id = Column(String, ForeignKey('trade_info.id'), nullable=False)
    posstatus = Column(String, nullable=True)
    cprice = Column(Float, nullable=True)
    ccost = Column(Float, nullable=True)
    cfee = Column(Float, nullable=True)
    cvol = Column(Float, nullable=True)
    cmargin = Column(Float, nullable=True)
    net = Column(Float, nullable=True)

    fk_trade = relationship("ModelTradeInfo", uselist=False, back_populates="fk_tradeHistory")
    
""" Explanation

    id: Unique identifier primary key
    trade_id: Not implemented, always return 0
    ordertxid: Order responsible for execution of trade.
    postxid: Position responsible for execution of trade.
    pair: Asset pair.
    time: Unix timestamp of trade.
    type: Type of order (buy/sell).
    ordertype: Order type.
    price: Average price order was executed at (quote currency).
    cost: Total cost of order (quote currency).
    fee: Total fee (quote currency).
    vol: Volume (base currency).
    margin: Initial margin (quote currency).
    leverage: Amount of leverage used in trade
    misc: Comma delimited list of miscellaneous info.
    maker: True if trade was executed with user as the maker, false if taker.
    posstatus: Position status (open/closed).
    cprice: Average price of closed portion of position (quote currency).
    ccost: Total cost of closed portion of position (quote currency).
    cfee: Total fee of closed portion of position (quote currency).
    cvol: Total volume of closed portion of position (base currency).
    cmargin: Total margin freed in closed portion of position (quote currency).
    net: Net profit/loss of closed portion of position (quote currency, quote currency scale).
"""
