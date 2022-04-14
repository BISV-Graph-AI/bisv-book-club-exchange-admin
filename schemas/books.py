from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# shared properties
class BookBase(BaseModel):
    title: str
    requirement: Optional[str] = None
    author: Optional[str] = None 
    isbn13: str
    isbn10: Optional[str] = None 
    editioncopyright: Optional[str] = None 
    publisher: Optional[str] = None 
    image: Optional[str] = None
    price: int
    status: int
    own: Optional[str] = None
    collection: Optional[str] = None
    uuid: Optional[str] = None
    seller_id: int
    date_added: Optional[date] = datetime.now().date()


# this will be used to validate data while creating a book 
class BookCreate(BookBase):
    title: str
    requirement: Optional[str] = None
    author: Optional[str] = None
    isbn13: str
    isbn10: Optional[str] = None
    editioncopyright: Optional[str] = None
    publisher: Optional[str] = None
    image: Optional[str] = None
    price: int
    status: int
    own: Optional[str] = None
    collection: Optional[str] = None
    uuid: Optional[str] = None
    seller_id: int
    date_added: Optional[date] = datetime.now().date()


# this will be used to format the response to not to have id, owner_id etc
class ShowBook(BookBase):
    title: str
    requirement: Optional[str] = None
    author: Optional[str] = None
    isbn13: str
    isbn10: Optional[str] = None
    editioncopyright: Optional[str] = None
    publisher: Optional[str] = None
    image: Optional[str] = None
    price: int
    status: int
    own: Optional[str] = None
    collection: Optional[str] = None
    uuid: Optional[str] = None
    seller_id: int
    date_added: Optional[date] = datetime.now().date()

    class Config:  # to convert non dict obj to json
        orm_mode = True
