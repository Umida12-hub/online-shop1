from pydantic import BaseModel
from pydantic import BaseModel
from typing import List

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int

class OrderOut(BaseModel):
    id: int
    owner: str
    total_price: float
    items: List[OrderItemOut]

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    pass