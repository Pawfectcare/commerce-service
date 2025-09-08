from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CartBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(..., ge=1)

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=1)

class CartOut(CartBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
