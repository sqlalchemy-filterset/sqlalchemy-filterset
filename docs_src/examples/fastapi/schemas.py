import uuid

from pydantic import BaseModel


class ProductOut(BaseModel):
    id: uuid.UUID
    name: str
    price: float
    is_active: bool

    class Config:
        orm_mode = True
