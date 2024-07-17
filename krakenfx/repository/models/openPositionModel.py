# krakenfx/api/models/openPositionModel.py
from sqlalchemy import Column, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from krakenfx.repository.models import Base


class ModelOpenPosition(Base):
    __tablename__ = "open_positions"

    trade_id = Column(
        String, primary_key=True, index=True, nullable=True
    )  # Possible foreign key to Trades
    ordertxid = Column(String)  # Foreign Key to Orders
    posstatus = Column(String, nullable=True)
    pair = Column(
        String, ForeignKey("consolidated_open_positions.pair"), nullable=False
    )
    time = Column(Float, nullable=True)
    type = Column(String, nullable=False)
    ordertype = Column(String, nullable=True)
    cost = Column(String, nullable=False)
    fee = Column(String, nullable=False)
    vol = Column(String, nullable=False)
    vol_closed = Column(String, nullable=False)
    margin = Column(String, nullable=False)
    terms = Column(String, nullable=True)
    rollovertm = Column(String, nullable=True)
    value = Column(String, nullable=True)
    net = Column(String, nullable=False)
    misc = Column(Text, nullable=True)
    oflags = Column(Text, nullable=True)

    def __repr__(self):
        return f"OpenPosition(pair={self.pair}, cost={self.cost}, vol={self.vol}, value={self.value})"


class ModelConsolidatedOpenPosition(Base):
    __tablename__ = "consolidated_open_positions"

    pair = Column(String, primary_key=True, index=True, nullable=True)
    positions = Column(String)
    type = Column(String)
    leverage = Column(String)
    cost = Column(String)
    fee = Column(String)
    vol = Column(String)
    vol_closed = Column(String)
    margin = Column(String)
    value = Column(String)
    net = Column(String)

    fk_openPositions = relationship("ModelOpenPosition", uselist=False)

    def __repr__(self):
        return f"ConsolidatedOpenPosition(pair={self.pair}, positions={self.positions}, value={self.value}, net={self.net})"
