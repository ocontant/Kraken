from sqlalchemy import Column, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from krakenfx.repository.models import Base

class ModelOrdersDescription(Base):                                                  
    __tablename__ = 'orders_descriptions'
    
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
        return f"ConsolidatedOpenPosition(id={self.id}, pair={self.pair}, price={self.price})"

class ModelOrders(Base):
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True)
    refid = Column(String, nullable=True)
    userref = Column(String, nullable=True)
    status = Column(String, nullable=False)
    opentm = Column(Float, nullable=False)
    closetm = Column(Float, nullable=True)
    starttm = Column(Float, nullable=True)
    expiretm = Column(Float, nullable=True)
    descr_id = Column(String, ForeignKey('orders_descriptions.id'), nullable=False)
    vol = Column(String, nullable=False)
    vol_exec = Column(String, nullable=False)
    cost = Column(String, nullable=False)
    fee = Column(String, nullable=False)
    price = Column(String, nullable=False)
    stopprice = Column(String, nullable=False)
    limitprice = Column(String, nullable=False)
    misc = Column(String, nullable=True)
    oflags = Column(String, nullable=False)
    margin = Column(String, nullable=True)
    reason = Column(String, nullable=True)

    fk_descr = relationship("ModelOrdersDescription",  uselist=False, back_populates="fk_orders")

    def __repr__(self):
        return f"ConsolidatedOpenPosition(id={self.id}, status={self.status}, cost={self.cost}, price={self.price})"