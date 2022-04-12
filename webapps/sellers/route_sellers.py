from typing import Optional

from apis.version1.route_login import get_current_user_from_token
from db.models.users import Users
from db.repository.sellers import create_new_seller
from db.repository.sellers import list_sellers
from db.repository.sellers import retreive_seller
from db.repository.sellers import search_seller
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from schemas.sellers import SellerCreate
from sqlalchemy.orm import Session
from webapps.sellers.forms import SellerCreateForm


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)



"""
@router.get("/")
async def home(request: Request, db: Session = Depends(get_db), msg: str = None):
    sellers = list_sellers(db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "sellers": sellers, "msg": msg}
    )
"""

@router.get("/details/{id}")
def seller_detail(id: int, request: Request, db: Session = Depends(get_db)):
    seller = retreive_seller(id=id, db=db)
    return templates.TemplateResponse(
        "sellers/detail.html", {"request": request, "seller": seller}
    )


@router.get("/post-a-seller/")
def create_seller(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("sellers/create_seller.html", {"request": request})


@router.post("/post-a-seller/")
async def create_seller(request: Request, db: Session = Depends(get_db)):
    form = SellerCreateForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )  # scheme will hold "Bearer" and param will hold actual token value
            current_user: User = get_current_user_from_token(token=param, db=db)
            seller = SellerCreate(**form.__dict__)
            seller = create_new_seller(seller=seller, db=db, owner_id=current_user.id)
            return responses.RedirectResponse(
                f"/details/{seller.id}", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "You might not be logged in, In case problem persists please contact us."
            )
            return templates.TemplateResponse("sellers/create_seller.html", form.__dict__)
    return templates.TemplateResponse("sellers/create_seller.html", form.__dict__)


@router.get("/delete-seller/")
def show_sellers_to_delete(request: Request, db: Session = Depends(get_db)):
    sellers = list_sellers(db=db)
    return templates.TemplateResponse(
        "sellers/show_sellers_to_delete.html", {"request": request, "sellers": sellers}
    )


@router.get("/search/")
def search(
    request: Request, db: Session = Depends(get_db), query: Optional[str] = None
):
    sellers = search_seller(query, db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "sellers": sellers}
    )
