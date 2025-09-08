from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum

class OrderStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

# Order Schemas
class OrderBase(BaseModel):
    user_id: int
    total_amount: float = Field(..., ge=0)
    status: OrderStatus = OrderStatus.PENDING_PAYMENT

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int


    class Config:
        orm_mode = True

# Payment Schemas
class PaymentBase(BaseModel):
    order_id: int
    amount: float = Field(..., ge=0)
    provider: str
    status: PaymentStatus
    transaction_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int


    class Config:
        orm_mode = True
