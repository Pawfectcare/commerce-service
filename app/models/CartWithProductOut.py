from pydantic import BaseModel

class CartWithProductOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product_name: str
    price: float

    class Config:
        orm_mode = True
