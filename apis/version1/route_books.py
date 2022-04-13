from typing import List
from typing import Optional

from apis.version1.route_login import get_current_user_from_token
from db.models.users import Users
from db.repository.books import create_new_book
from db.repository.books import delete_book_by_id
from db.repository.books import list_books
from db.repository.books import retreive_book
from db.repository.books import search_book
from db.repository.books import update_book_by_id
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.templating import Jinja2Templates
from schemas.books import BookCreate
from schemas.books import ShowBook
from sqlalchemy.orm import Session


router = APIRouter()
templates = Jinja2Templates(directory="templates")



@router.post("/create-book/", response_model=ShowBook)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db)
):
    book = create_new_book(book=book, db=db)
    return book 


@router.get(
    "/get/{id}", response_model=ShowBook
)  # if we keep just "{id}" . it would stat catching all routes
def read_book(id: int, db: Session = Depends(get_db)):
    book = retreive_book(id=id, db=db)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with this id {id} does not exist",
        )
    return book 


@router.get("/all", response_model=List[ShowBook])
def read_books(db: Session = Depends(get_db)):
    books = list_books(db=db)
    return books


@router.put("/update/{id}")
def update_book(id: int, book: BookCreate, db: Session = Depends(get_db)):
    current_user = 1
    message = update_book_by_id(id=id, book=book, db=db)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {id} not found"
        )
    return {"msg": "Successfully updated data."}


@router.delete("/delete/{id}")
def delete_book(
    id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_from_token),
):
    book = retreive_book(id=id, db=db)
    if not book:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {id} does not exist",
        )
    delete_book_by_id(id=id, db=db)
    return {"detail": "Successfully deleted."}
    

@router.get("/books_autocomplete")
def autocomplete(term: Optional[str] = None, db: Session = Depends(get_db)):
    books = search_book(term, db=db)
    book_names = []
    for book in books:
        book_names.append(book.name)
    return book_names
