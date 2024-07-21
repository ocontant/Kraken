from sqlalchemy import Boolean, Column, Float, Integer, String

from krakenfx.repository.models._base import Base

# from sqlalchemy.orm import relationship


# from krakenfx.repository.models.associationsTablesModel import order_trade_association


class ModelTradeInfo(Base):
    __tablename__ = "trade_info"

    id = Column(String, primary_key=True, index=True, nullable=True)
    trade_id = Column(Integer, nullable=False)  # Unused, always 0
    ordertxid = Column(String, nullable=False)
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
    posstatus = Column(String, nullable=True)
    cprice = Column(Float, nullable=True)
    ccost = Column(Float, nullable=True)
    cfee = Column(Float, nullable=True)
    cvol = Column(Float, nullable=True)
    cmargin = Column(Float, nullable=True)
    net = Column(Float, nullable=True)
    trades = Column(String, nullable=True)

    # Issue building relations between tables:
    ## Error: Failed: General exception occurred: greenlet_spawn has not been called; can't call await_only() here.
    ##                Was IO attempted in an unexpected place?
    ## References: https://stackoverflow.com/questions/74252768/missinggreenlet-greenlet-spawn-has-not-been-called

    # rel_orders = relationship(
    #     "ModelOrders",
    #     secondary=order_trade_association,
    #     back_populates="rel_trades",
    #     lazy="subquery",
    # )
    """
    Model for the Trades:

    Attributes:
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
