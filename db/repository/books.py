from db.models.books import Books
from schemas.books import BookCreate
from sqlalchemy.orm import Session



def create_new_book(book: BookCreate, db: Session):
    book = Books(
        title=book.title,
        requirement=book.requirement,
        author=book.author,
        isbn13=book.isbn13,
        isbn10=book.isbn10,
        editioncopyright=book.editioncopyright,
        publisher=book.publisher,
        image=book.image,
        price=book.price,
        status=book.status,
        own=book.own,
        collection=book.collection,
        uuid=book.uuid,
        seller_id=book.seller_id,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book 

def retreive_book(id: int, db: Session):
    item = db.query(Books).filter(Books.id == id).first()
    return item

def retreive_book_by_uuid(uuid: str, db: Session):
    item = db.query(Books).filter(Books.uuid == uuid)
    return item


def list_books(db: Session):
    books = db.query(Books).all()
    return books


def update_book_by_id(id: int, book: BookCreate, db: Session):
    existing_book = db.query(Books).filter(Books.id == id)
    if not existing_book.first():
        return 0
    existing_book.update(book.__dict__)
    db.commit()
    db.refresh(existing_book)
    return 1


def delete_book_by_id(id: int, db: Session):
    existing_book = db.query(Books).filter(Books.id == id)
    if not existing_book.first():
        return 0
    existing_book.delete(synchronize_session=False)
    db.commit()
    return 1


def search_book(query: str, db: Session):
    books = db.query(Books).filter(Books.title.contains(query))
    return books
