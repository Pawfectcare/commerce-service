from pydantic import BaseModel, Field
from typing import Optional



class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=50, description="Product category: food, toys, grooming")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)


class ProductOut(ProductBase):
    id: int


    class Config:
        orm_mode = True
