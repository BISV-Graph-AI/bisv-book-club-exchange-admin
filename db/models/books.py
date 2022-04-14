from db.base_class import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship


class Books(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    requirement = Column(String)
    author = Column(String)
    isbn13 = Column(String, nullable=False)
    isbn10 = Column(String)
    editioncopyright = Column(String)
    publisher = Column(String)
    image = Column(String)
    price = Column(Integer)
    status = Column(Integer)
    own = Column(String)
    collection = Column(String)
    uuid = Column(String)
    date_added = Column(Date)
    seller_id = Column(Integer, ForeignKey("sellers.id"))
    seller = relationship("Sellers", back_populates="books")
