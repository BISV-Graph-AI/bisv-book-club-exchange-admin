from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr


# shared properties
class SellerBase(BaseModel):
    name: str 
    email: EmailStr
    paypal: Optional[str] = None
    zelle: Optional[str] = None
    collection: str
    date_added: Optional[date] = datetime.now().date()


# this will be used to validate data while creating a seller 
class SellerCreate(SellerBase):
    email: str


# this will be used to format the response to not to have id, owner_id etc
class ShowSeller(SellerBase):
    name: str
    email: EmailStr
    paypal: str
    collection: str
    date_added: Optional[date] = datetime.now().date()

    class Config:  # to convert non dict obj to json
        orm_mode = True
