from sqlalchemy import Column, ForeignKey, String, Table

from krakenfx.repository.models._base import Base

# Define the association table
order_trade_association = Table(
    "order_trade_association",
    Base.metadata,
    Column("order_id", String, ForeignKey("orders.id"), primary_key=True),
    Column("trade_id", String, ForeignKey("trade_info.id"), primary_key=True),
)
