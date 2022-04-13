from typing import Optional

from apis.version1.route_login import get_current_user_from_token
from db.models.users import Users
from db.repository.books import create_new_book
from db.repository.books import list_books
from db.repository.books import retreive_book
from db.repository.books import search_book
from db.repository.books import update_book_by_id
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from schemas.books import BookCreate
from sqlalchemy.orm import Session
from webapps.books.forms import BookCreateForm


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)



def get_bookinfo_by_isbn(raw_isbn13):
    import json
    import requests
    import xml.etree.ElementTree as et

    numeric_filter = filter(str.isdigit, raw_isbn13)
    isbn13 = ''.join(numeric_filter)
    bookinfo = {
        'isbn13': isbn13,
        'isbn10': '',
        'author': '',
        'title': '',
        'publisher': '',
        'image': ''
    }
    try:
        url = 'https://openlibrary.org/api/books?bibkeys=ISBN:{}&jscmd=details&format=json'.format(isbn13)
        response = requests.get(url)
        #print(response.json())
        #book_dict = json.loads(response.json())
        book_dict = response.json()
        for key in book_dict.keys():
            value = book_dict[key]
            for subkey in value:
                subvalue = value[subkey]
                if (subkey == 'thumbnail_url'):
                    bookinfo['image'] = subvalue
                if (subkey == 'details'):
                    for detail in subvalue:
                        if (detail == 'title'):
                            bookinfo['title'] = subvalue[detail]
                        if (detail == 'publishers'):
                            if (len(subvalue[detail]) > 0):
                                bookinfo['publisher'] = subvalue[detail][0]
                        if (detail == 'isbn_10'):
                            if (len(subvalue[detail]) > 0):
                                bookinfo['isbn10'] = subvalue[detail][0]
                        if (detail == 'authors'):
                            if (len(subvalue[detail]) > 0):
                                author = subvalue[detail][0]
                                if ('name' in author.keys()):
                                    bookinfo['author'] = author['name']
    except Exception as err:
        print('Exception: ' + str(err))
    return bookinfo


@router.get("/getbookinfo/{isbn13}")
async def getbookinfo(isbn13: str):
    return get_bookinfo_by_isbn(isbn13) 

"""
@router.get("/")
async def home(request: Request, db: Session = Depends(get_db), msg: str = None):
    books = list_books(db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "books": books, "msg": msg}
    )
"""

@router.get("/list-all-books/")
def list_all_books(request: Request, db: Session = Depends(get_db)):
    books = list_books(db=db)
    return templates.TemplateResponse(
        "books/list_all_books.html", {"request": request, "books": books}
    )

@router.get("/books/{id}")
def book_detail(id: int, request: Request, db: Session = Depends(get_db)):
    book = retreive_book(id=id, db=db)
    return templates.TemplateResponse(
        "books/detail.html", {"request": request, "book": book}
    )


@router.get("/post-a-book/")
def create_book(request: Request, db: Session = Depends(get_db)):
    books = list_books(db=db)
    return templates.TemplateResponse("books/create_book.html", {"request": request, "books": books})


@router.post("/post-a-book/")
async def create_book(request: Request, db: Session = Depends(get_db)):
    form = BookCreateForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_user: User = get_current_user_from_token(token=param, db=db)
            book = BookCreate(**form.__dict__)
            book = create_new_book(book=book, db=db)
            return responses.RedirectResponse(
                f"/details/{book.id}", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "You might not be logged in, In case problem persists please contact us."
            )
            return templates.TemplateResponse("books/create_book.html", form.__dict__)
    return templates.TemplateResponse("books/create_book.html", form.__dict__)


@router.get("/edit-a-book/{id}")
def edit_book(id: int, request: Request, db: Session = Depends(get_db)):
    book = retreive_book(id=id, db=db)
    return templates.TemplateResponse(
        "books/edit_book.html", {"request": request, "book": book}
    )


@router.post("/edit-a-book/{id}")
async def update_book(id: int, request: Request, db: Session = Depends(get_db)):
    form = BookCreateForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_user: User = get_current_user_from_token(token=param, db=db)
            book = BookCreate(**form.__dict__)
            book = update_book_by_id(id=id, book=book, db=db)
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "You might not be logged in, In case problem persists please contact us."
            )
            return templates.TemplateResponse("general_pages/homepage.html", form.__dict__)
    book = retreive_book(id=id, db=db)
    return templates.TemplateResponse(
        "books/edit_book.html", {"request": request, "book": book}
    )


@router.get("/delete-book/")
def show_books_to_delete(request: Request, db: Session = Depends(get_db)):
    books = list_books(db=db)
    return templates.TemplateResponse(
        "books/show_books_to_delete.html", {"request": request, "books": books}
    )


@router.get("/search-book/")
def search(
    request: Request, db: Session = Depends(get_db), query: Optional[str] = None
):
    books = search_book(query, db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "books": books}
    )
