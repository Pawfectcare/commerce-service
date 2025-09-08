from sqlalchemy import Column, Integer, String, Numeric, func
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, server_default='0')
    category = Column(String, nullable=False, index=True)  # food, toys, grooming

