import chardet
import csv
import math
import os

from typing import List
from typing import Optional

from apis.version1.route_login import get_current_user_from_token
from core.security import get_api_key
from db.models.users import Users
from db.repository.books import create_new_book
from db.repository.books import list_books
from db.repository.books import retreive_book
from db.repository.books import retreive_book_by_uuid
from db.repository.books import search_book
from db.repository.books import update_book_by_id
from db.repository.sellers import create_new_seller
from db.repository.sellers import get_seller_id_from_collection
from db.repository.sellers import list_sellers
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import UploadFile
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.api_key import APIKey
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from schemas.books import BookCreate
from schemas.sellers import SellerCreate
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
async def home(request: Request, db: Session = Depends(get_db), msg: str = None, api_key: APIKey = Depends(get_api_key)):
    books = list_books(db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "books": books, "msg": msg}
    )
"""

@router.get("/list-all-books/")
def list_all_books(request: Request, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    books = list_books(db=db)
    return templates.TemplateResponse(
        "books/list_all_books.html", {"request": request, "books": books}
    )

@router.get("/books/{id}")
def book_detail(id: int, request: Request, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    book = retreive_book(id=id, db=db)
    return templates.TemplateResponse(
        "books/detail.html", {"request": request, "book": book}
    )


@router.get("/post-a-book/")
def create_book(request: Request, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    sellers = list_sellers(db=db)
    return templates.TemplateResponse("books/create_book.html", {"request": request, "sellers": sellers})


@router.post("/post-a-book/")
async def create_book(request: Request, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
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
def edit_book(id: int, request: Request, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    book = retreive_book(id=id, db=db)
    return templates.TemplateResponse(
        "books/edit_book.html", {"request": request, "book": book}
    )


@router.post("/edit-a-book/{id}")
async def update_book(id: int, request: Request, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
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
def show_books_to_delete(request: Request, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
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


def delete_file(file_path):
   if (os.path.exists(file_path)):
       os.remove(file_path)

header_column_map = {
    '#isbn': 'isbn13',
    'isbn#': 'isbn13',
    'isbn': 'isbn13',
    'author': 'author',
    'copyright': 'editioncopyright',
    'publisher': 'publisher',
    'own': 'own',
    'collection': 'collection',
    'price': 'price',
    'recordUUID': 'uuid',
    'title': 'title'
}

def import_book(header_dict, row, db, owner_id):
    created = False
    row_isbn = ''
    row_uuid = ''
    try:
        book = {
            'title': '',
            'requirement': '',
            'author': '',
            'isbn13': '',
            'isbn10': '',
            'editioncopyright': '',
            'publisher': '',
            'image': '',
            'price': 0,
            'status': 1,
            'own': '',
            'collection': '',
            'uuid': '',
            'seller_id': 0,   
        } 

        for col_index, col in enumerate(row):
            for key in book.keys():
                if (header_dict[col_index] in header_column_map.keys()):
                    book[header_column_map[header_dict[col_index]]] = col
        row_isbn = book['isbn13']
        row_uuid = book['uuid']

        # Check book with UUID, skip it the book exists, ignore the book with empty isbn
        existing_book = retreive_book_by_uuid(book['uuid'], db)
        isbn13_str = str(book['isbn13'])
        if (existing_book is not None and not existing_book.first() and isbn13_str.strip() != ''):
            # Round price
            try:
                str_price = str(book['price'])
                if (len(str_price.strip()) > 0):
                    price = float(str_price)
                    book['price'] = math.ceil(price)
            except Exception:
                book['price'] = 0

            # Make the book available
            book['status'] = 1

            # Get seller ID by collection
            try:
                if (book['collection'].strip() != ''):
                    seller = get_seller_id_from_collection(book['collection'].strip(), db)
                    if (seller is not None and seller.first()):
                        book['seller_id'] = seller.first().id
            except Exception:
                book['seller_id'] = 0

            # Create a new seller and get seller ID
            if (book['seller_id'] == 0):
                new_sellercreate = SellerCreate(
                    name='No Name',
                    email='No Email',
                    paypal='',
                    zelle='',
                    collection='',
                    owner_id=owner_id 
                )
                new_seller = create_new_seller(seller=new_sellercreate, db=db, owner_id=owner_id)
                book['seller_id'] = new_seller.id 

            # Create a book
            new_bookcreate = BookCreate(
                title=book['title'],
                requirement=book['requirement'],
                author=book['author'],
                isbn13=book['isbn13'],
                isbn10=book['isbn10'],
                editioncopyright=book['editioncopyright'],
                publisher=book['publisher'],
                image=book['image'],
                price=book['price'],
                status=book['status'],
                own=book['own'],
                collection=book['collection'],
                uuid=book['uuid'],
                seller_id=book['seller_id']
            )
            new_book = create_new_book(book=new_bookcreate, db=db)
            created = True
    except Exception as err:
        created = False
        print('import_book Exception: ' + str(err))
    return created, row_isbn, row_uuid

def upload_books_from_csv(request, files, db, owner_id):
    errors = []
    csv_path = 'tmp'
    for file in files:
        csv_name = file.filename
        file_path = os.path.join(os.path.sep, csv_path, csv_name)
        try:
            # Write uploaded file to /tmp/
            with open(file_path, mode='wb+') as f:
                f.write(file.file.read())

            # Detect file encoding, default is ISO-8859-1
            encoding = 'ISO-8859-1'
            with open(file_path, 'rb') as file:
                codec_dict = chardet.detect(file.read())
                if (codec_dict is not None and 'encoding' in codec_dict):
                    encoding = codec_dict['encoding']

            # Open CSV, parse line by line to import into books
            header_dict = {}
            with open(file_path, mode='r', encoding=encoding) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if (line_count == 0):
                        for col_index, col in enumerate(row):
                            header_dict[col_index] = col
                    if (line_count > 0):
                        created, row_isbn, row_uuid = import_book(header_dict, row, db, owner_id)
                        if (not created):
                            errors.append('ISBN: {} UUID: {} existed. Skipped.'.format(row_isbn, row_uuid))
                    line_count += 1

            # Send to Gmail for storage
            # TODO:

            delete_file(file_path)
        except Exception as err:
            delete_file(file_path)
            errors.append(csv_name + ' has issues: ' + str(err))
    return errors

@router.get("/upload-books-from-csv/")
def get_upload_books_from_csv(request: Request, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    return templates.TemplateResponse(
        "books/upload_books_from_csv.html", {"request": request}
    )

@router.post("/upload-books-from-csv/")
async def post_upload_books_from_csv(request: Request, files: List[UploadFile], db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    errors = []
    try:
        token = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(
            token
        )  # scheme will hold "Bearer" and param will hold actual token value
        current_user: User = get_current_user_from_token(token=param, db=db)
        errors = upload_books_from_csv(request=request, files=files, db=db, owner_id=current_user.id)
        if (len(errors) > 0):
            return templates.TemplateResponse("books/upload_books_from_csv.html", {"request": request, "errors": errors})
        else:
            return responses.RedirectResponse(
                f"/list-all-books", status_code=status.HTTP_302_FOUND
            )
    except Exception as e:
        print(e)
        errors.append(
            "You might not be logged in, In case problem persists please contact us."
        )
        return templates.TemplateResponse("general_pages/homepage.html", {"request": request, "errors": errors})

    return templates.TemplateResponse("books/upload_books_from_csv.html", {"request": request, "errors": errors})

