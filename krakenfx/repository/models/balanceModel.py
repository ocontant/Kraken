from sqlalchemy import Column, String

from krakenfx.repository.models._base import Base


class ModelBalance(Base):
    __tablename__ = "balances"

    asset = Column(String, primary_key=True)
    amount = Column(String, nullable=False)
