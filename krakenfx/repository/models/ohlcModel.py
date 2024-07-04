from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    BigInteger,
    ForeignKey,
    Index,
    create_engine,
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

Base = declarative_base()


class AssetPair(Base):
    __tablename__ = "asset_pairs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

    ohlc_data = relationship("OHLCData", back_populates="asset_pair")
    ohlc_results = relationship("OHLCResult", back_populates="asset_pair")

    def __init__(self, name):
        self.name = name


class OHLCData(Base):
    __tablename__ = "ohlc_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_pair_id = Column(Integer, ForeignKey("asset_pairs.id"), nullable=False)
    time = Column(BigInteger, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    vwap = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)

    asset_pair = relationship("AssetPair", back_populates="ohlc_data")

    def __init__(
        self, asset_pair_id, time, open, high, low, close, vwap, volume, count
    ):
        self.asset_pair_id = asset_pair_id
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.vwap = vwap
        self.volume = volume
        self.count = count


# Adding index to improve query performance
Index("idx_asset_pair_time", OHLCData.asset_pair_id, OHLCData.time)


class OHLCResult(Base):
    __tablename__ = "ohlc_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_pair_id = Column(Integer, ForeignKey("asset_pairs.id"), nullable=False)
    last = Column(BigInteger, nullable=False)

    asset_pair = relationship("AssetPair", back_populates="ohlc_results")

    def __init__(self, asset_pair_id, last):
        self.asset_pair_id = asset_pair_id
        self.last = last
