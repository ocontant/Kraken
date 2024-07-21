from sqlalchemy import JSON, Column, String
from sqlalchemy.dialects.postgresql import JSONB

from krakenfx.repository.models._base import Base


class ModelAssetsPairs(Base):
    __tablename__ = "assets_pairs"

    pair_name = Column(String, primary_key=True, nullable=False)
    data = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False)
