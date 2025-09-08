from sqlalchemy import (
    Column,
    Integer,
    # DateTime removed
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    func
)
from app.core.database import Base

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, server_default='1')


    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='_user_product_uc'),
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )
