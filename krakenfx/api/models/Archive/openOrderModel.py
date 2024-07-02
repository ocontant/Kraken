from sqlalchemy import Column, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from krakenfx.core.database import Base

class ModelOpenOrderDescription(Base):                                                  
    __tablename__ = 'open_order_descriptions'
    
    id = Column(String, primary_key=True)
    pair = Column(String, nullable=False)
    type = Column(String, nullable=False)
    ordertype = Column(String, nullable=False)
    price = Column(String, nullable=False)
    price2 = Column(String, nullable=False)
    leverage = Column(String, nullable=False)
    order = Column(Text, nullable=False)
    close = Column(Text, nullable=False)
    
    fk_open_order = relationship("ModelOpenOrder", uselist=False, back_populates="fk_descr")

class ModelOpenOrder(Base):
    __tablename__ = 'open_order'
    
    id = Column(String, primary_key=True)
    refid = Column(String, nullable=True)
    userref = Column(String, nullable=True)
    status = Column(String, nullable=False)
    opentm = Column(Float, nullable=False)
    starttm = Column(Float, nullable=False)
    expiretm = Column(Float, nullable=False)
    descr_id = Column(String, ForeignKey('open_order_descriptions.id'), nullable=False)
    vol = Column(String, nullable=False)
    vol_exec = Column(String, nullable=False)
    cost = Column(String, nullable=False)
    fee = Column(String, nullable=False)
    price = Column(String, nullable=False)
    stopprice = Column(String, nullable=False)
    limitprice = Column(String, nullable=False)
    misc = Column(String, nullable=True)
    oflags = Column(String, nullable=False)

    fk_descr = relationship("ModelOpenOrderDescription",  uselist=False, back_populates="fk_open_order")

