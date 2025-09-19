from sqlalchemy import Column, Integer, Numeric, JSON, ForeignKey
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    cart = Column(JSON, nullable=False)   # store the whole cart array
    total = Column(Numeric(10, 2), nullable=False)
