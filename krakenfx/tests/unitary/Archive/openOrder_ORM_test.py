import pytest
from sqlalchemy import create_engine, Column, String, Float, Text, ForeignKey, JSON, MetaData
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Define new metadata for testing
test_metadata = MetaData()
Base = declarative_base(metadata=test_metadata)

# ORM models for testing
class OpenOrderDescriptionModel(Base):
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

class OpenOrderModel(Base):
    __tablename__ = 'open_orders'
    
    id = Column(String, primary_key=True)
    refid = Column(String)
    userref = Column(String)
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
    misc = Column(String, nullable=False)
    oflags = Column(String, nullable=False)
    trades = Column(JSON)  # Use JSON for SQLite

    descr = relationship("OpenOrderDescriptionModel")

@pytest.fixture(scope='function')
def session():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_orm_mapping(session):
    open_order_data = {
        "O66CFS-PILNI-MEQWTR": {
            "refid": "OT12345-ABC",
            "userref": "12345",
            "status": "open",
            "opentm": 1717608049.2375944,
            "starttm": 0,
            "expiretm": 0,
            "descr": {
                "pair": "XXBTZUSD",
                "type": "buy",
                "ordertype": "market",
                "price": "45000.0",
                "price2": "0.0",
                "leverage": "none",
                "order": "buy 2.00000000 XXBTUSD @ market",
                "close": "sell 2.00000000 XXBTUSD @ 50000.0"
            },
            "vol": "2.00000000",
            "vol_exec": "0.00000000",
            "cost": "90000.0",
            "fee": "90.0",
            "price": "45000.0",
            "stopprice": "0.0",
            "limitprice": "0.0",
            "misc": "",
            "oflags": "fciq",
            "trades": ["TT12345", "TT67890"]
        }
    }

    for order_id, order_data in open_order_data.items():
        descr_data = order_data["descr"]
        
        # Create OpenOrderDescriptionModel instance
        descr = OpenOrderDescriptionModel(
            id=order_id,
            pair=descr_data["pair"],
            type=descr_data["type"],
            ordertype=descr_data["ordertype"],
            price=descr_data["price"],
            price2=descr_data["price2"],
            leverage=descr_data["leverage"],
            order=descr_data["order"],
            close=descr_data["close"],
        )
        
        # Add description to session
        session.add(descr)
        
        # Create OpenOrderModel instance
        order = OpenOrderModel(
            id=order_id,
            refid=order_data["refid"],
            userref=order_data["userref"],
            status=order_data["status"],
            opentm=order_data["opentm"],
            starttm=order_data["starttm"],
            expiretm=order_data["expiretm"],
            descr_id=order_id,
            vol=order_data["vol"],
            vol_exec=order_data["vol_exec"],
            cost=order_data["cost"],
            fee=order_data["fee"],
            price=order_data["price"],
            stopprice=order_data["stopprice"],
            limitprice=order_data["limitprice"],
            misc=order_data["misc"],
            oflags=order_data["oflags"],
            trades=order_data["trades"],
        )
        
        # Add order to session
        session.add(order)
    
    session.commit()

    # Verify data is correctly stored
    stored_order = session.query(OpenOrderModel).filter_by(id="O66CFS-PILNI-MEQWTR").one()
    assert stored_order.refid == "OT12345-ABC"
    assert stored_order.userref == "12345"
    assert stored_order.status == "open"
    assert stored_order.opentm == 1717608049.2375944
    assert stored_order.descr.pair == "XXBTZUSD"
    assert stored_order.descr.type == "buy"
    assert stored_order.descr.ordertype == "market"
    assert stored_order.descr.price == "45000.0"
    assert stored_order.descr.price2 == "0.0"
    assert stored_order.descr.leverage == "none"
