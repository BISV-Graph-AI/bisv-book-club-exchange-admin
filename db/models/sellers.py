from db.base_class import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class Sellers(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    paypal = Column(String)
    zelle = Column(String)
    date_added = Column(Date)
    is_active = Column(Boolean(), default=True)
    collection = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("Users", back_populates="sellers")
    books = relationship("Books", back_populates="seller")
