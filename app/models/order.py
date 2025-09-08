from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship

from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, nullable=False, server_default="PENDING_PAYMENT")
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    payments = relationship("Payment", back_populates="order")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    provider = Column(String, nullable=False)
    status = Column(String, nullable=False)
    transaction_id = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    order = relationship("Order", back_populates="payments")
