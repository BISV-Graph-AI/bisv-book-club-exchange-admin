from typing import List
from typing import Optional

from fastapi import Request


class BookCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.title: str
        self.requirement: str
        self.author: str
        self.isbn13: str
        self.isbn10: str
        self.editioncopyright: str
        self.publisher: str
        self.image: str
        self.price: int
        self.status: int 
        self.own: str
        self.collection: str
        self.uuid: str
        self.seller_id: int

    async def load_data(self):
        form = await self.request.form()
        self.title = form.get("title")
        self.requirement = form.get("requirement")
        self.author = form.get("author")
        self.isbn13 = form.get("isbn13")
        self.isbn10 = form.get("isbn10")
        self.editioncopyright = form.get("editioncopyright")
        self.publisher = form.get("publisher")
        self.image = form.get("image")
        self.price = form.get("price")
        self.status = form.get("status")
        self.own = form.get("own")
        self.collection = form.get("collection")
        self.uuid = form.get("uuid")
        self.seller_id = form.get("seller_id")

    def is_valid(self):
        if not self.isbn13 or not len(self.isbn13) < 13:
            self.errors.append("A valid ISBN is required")
        if not self.seller_id:
            self.errors.append("Valid Seller ID is required")
        if not self.errors:
            return True
        return False
