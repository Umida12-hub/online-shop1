from pydantic import BaseModel
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None  

class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None   

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None