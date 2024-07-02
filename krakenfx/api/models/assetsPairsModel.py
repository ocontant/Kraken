from sqlalchemy import Column, Integer, Float, String, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from krakenfx.core.database import Base 


# Association table for fees and asset pairs
fees_table = Table(
    'fees', Base.metadata,
    Column('asset_pair_id', Integer, ForeignKey('model_asset_pair_details.id')),
    Column('fee_schedule_id', Integer, ForeignKey('model_fee_schedules.id'))
)

fees_maker_table = Table(
    'fees_maker', Base.metadata,
    Column('asset_pair_id', Integer, ForeignKey('model_asset_pair_details.id')),
    Column('fee_schedule_id', Integer, ForeignKey('model_fee_schedules.id'))
)

class ModelFeeSchedule(Base):
    __tablename__ = 'model_fee_schedules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    volume = Column(Integer, nullable=False)
    fee = Column(Float, nullable=False)

class ModelAssetPairDetails(Base):
    __tablename__ = 'model_asset_pair_details'

    id = Column(Integer, primary_key=True)
    altname = Column(String, nullable=False)
    wsname = Column(String, nullable=False)
    aclass_base = Column(String, nullable=False)
    base = Column(String, nullable=False)
    aclass_quote = Column(String, nullable=False)
    quote = Column(String, nullable=False)
    lot = Column(String, nullable=False)
    cost_decimals = Column(Integer, nullable=False)
    pair_decimals = Column(Integer, nullable=False)
    lot_decimals = Column(Integer, nullable=False)
    lot_multiplier = Column(Integer, nullable=False)
    fee_volume_currency = Column(String, nullable=False)
    margin_call = Column(Integer, nullable=False)
    margin_stop = Column(Integer, nullable=False)
    ordermin = Column(String, nullable=False)
    costmin = Column(String, nullable=False)
    tick_size = Column(String, nullable=False)
    status = Column(String, nullable=False)
    long_position_limit = Column(Integer, nullable=True)
    short_position_limit = Column(Integer, nullable=True)

    leverage_buy = Column(String, nullable=False)  # Storing as comma-separated values
    leverage_sell = Column(String, nullable=False)  # Storing as comma-separated values

    fees = relationship('ModelFeeSchedule', secondary=fees_table, backref='asset_pairs')
    fees_maker = relationship('ModelFeeSchedule', secondary=fees_maker_table, backref='maker_asset_pairs')

class ModelCollateralAssetDetails(Base):
    __tablename__ = 'model_collateral_asset_details'

    id = Column(Integer, primary_key=True)
    aclass = Column(String, nullable=False)
    altname = Column(String, nullable=False)
    decimals = Column(Integer, nullable=False)
    display_decimals = Column(Integer, nullable=False)
    collateral_value = Column(Float, nullable=True)
    status = Column(String, nullable=False)