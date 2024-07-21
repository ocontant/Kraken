from sqlalchemy import BigInteger, Column, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from krakenfx.repository.models._base import Base


class ModelOHLCAssetPair(Base):
    __tablename__ = "ohlc_asset_pairs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(
        String, ForeignKey("assets_pairs.pair_name"), unique=True, nullable=False
    )

    rel_ohlc_data = relationship("ModelOHLCData", back_populates="rel_asset_pair")
    rel_ohlc_results = relationship("ModelOHLCResult", back_populates="rel_asset_pair")

    def __init__(self, name):
        self.name = name


class ModelOHLCData(Base):
    __tablename__ = "ohlc_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_pair_id = Column(Integer, ForeignKey("ohlc_asset_pairs.id"), nullable=False)
    time = Column(BigInteger, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    vwap = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)

    rel_asset_pair = relationship("ModelOHLCAssetPair", back_populates="rel_ohlc_data")

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
Index("idx_ohlc_data_asset_pair_time", ModelOHLCData.asset_pair_id, ModelOHLCData.time)


class ModelOHLCResult(Base):
    __tablename__ = "ohlc_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_pair_id = Column(Integer, ForeignKey("ohlc_asset_pairs.id"), nullable=False)
    last = Column(BigInteger, nullable=False)

    rel_asset_pair = relationship(
        "ModelOHLCAssetPair", back_populates="rel_ohlc_results"
    )

    def __init__(self, asset_pair_id, last):
        self.asset_pair_id = asset_pair_id
        self.last = last
