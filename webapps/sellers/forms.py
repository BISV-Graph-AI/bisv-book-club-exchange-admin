from typing import List
from typing import Optional

from fastapi import Request


class SellerCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.name: str
        self.email: str
        self.paypal: Optional[str] = None
        self.zelle: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.name = form.get("name")
        self.email = form.get("email")
        self.paypal = form.get("paypal")
        self.zelle = form.get("zelle")

    def is_valid(self):
        if not self.name or not len(self.name) >= 4:
            self.errors.append("A valid name is required")
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Valid Email is required e.g. test@example.com")
        if not self.errors:
            return True
        return False
