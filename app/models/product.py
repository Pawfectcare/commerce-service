from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, server_default='0')
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
