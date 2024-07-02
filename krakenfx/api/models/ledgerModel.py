# my_project/api/models/ledger.py
from sqlalchemy import Column, String, Float
from krakenfx.core.database import Base

class ModelLedger(Base):
    __tablename__ = 'ledgers'

    id = Column(String, primary_key=True, index=True)
    aclass = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    asset = Column(String, nullable=False)
    balance = Column(String, nullable=False)
    fee = Column(String, nullable=False)
    refid = Column(String, nullable=False)
    time = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    subtype = Column(String, nullable=True)
