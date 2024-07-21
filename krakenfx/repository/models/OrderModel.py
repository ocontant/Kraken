from sqlalchemy import Column, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from krakenfx.repository.models._base import Base

# from krakenfx.repository.models.associationsTablesModel import order_trade_association


class ModelOrdersDescription(Base):
    __tablename__ = "orders_descriptions"

    id = Column(String, primary_key=True)
    pair = Column(String, nullable=False)
    type = Column(String, nullable=False)
    ordertype = Column(String, nullable=False)
    price = Column(String, nullable=False)
    price2 = Column(String, nullable=False)
    leverage = Column(String, nullable=True)
    order = Column(Text, nullable=False)
    close = Column(Text, nullable=True)

    fk_orders = relationship("ModelOrders", uselist=False, back_populates="fk_descr")

    def __repr__(self):
        return f"id={self.id}, pair={self.pair}, price={self.price}"


class ModelOrders(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    refid = Column(String, nullable=True)
    userref = Column(String, nullable=True)
    status = Column(String, nullable=False)
    opentm = Column(Float, nullable=False)
    closetm = Column(Float, nullable=True)
    starttm = Column(Float, nullable=True)
    expiretm = Column(Float, nullable=True)
    descr_id = Column(String, ForeignKey("orders_descriptions.id"), nullable=False)
    vol = Column(String, nullable=False)
    vol_exec = Column(String, nullable=False)
    cost = Column(String, nullable=False)
    fee = Column(String, nullable=False)
    price = Column(String, nullable=False)
    stopprice = Column(String, nullable=True)
    limitprice = Column(String, nullable=True)
    misc = Column(String, nullable=True)
    oflags = Column(String, nullable=False)
    margin = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    trades = Column(String, nullable=True)

    fk_descr = relationship(
        "ModelOrdersDescription",
        uselist=False,
        back_populates="fk_orders",
        lazy="selectin",
    )

    # Issue building relations between tables:
    ## Error: Failed: General exception occurred: greenlet_spawn has not been called; can't call await_only() here.
    ##                Was IO attempted in an unexpected place?
    ## References: https://stackoverflow.com/questions/74252768/missinggreenlet-greenlet-spawn-has-not-been-called

    # rel_trades = relationship(
    #     "ModelTradeInfo",
    #     secondary=order_trade_association,
    #     back_populates="rel_orders",
    #     lazy="subquery",
    # )

    def __repr__(self):
        return (
            f"id={self.id}, status={self.status}, cost={self.cost}, price={self.price}"
        )
