from typing import List
from typing import Optional

from apis.version1.route_login import get_current_user_from_token
from db.models.users import Users
from db.repository.sellers import create_new_seller
from db.repository.sellers import delete_seller_by_id
from db.repository.sellers import list_sellers
from db.repository.sellers import retreive_seller
from db.repository.sellers import search_seller
from db.repository.sellers import update_seller_by_id
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.templating import Jinja2Templates
from schemas.sellers import SellerCreate
from schemas.sellers import ShowSeller
from sqlalchemy.orm import Session


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/create-seller/", response_model=ShowSeller)
def create_seller(
    seller: SellerCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_from_token),
):
    seller = create_new_seller(seller=seller, db=db, owner_id=current_user.id)
    return seller 


@router.get(
    "/get_seller/{id}", response_model=ShowSeller
)  # if we keep just "{id}" . it would stat catching all routes
def read_seller(id: int, db: Session = Depends(get_db)):
    seller = retreive_seller(id=id, db=db)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seller with this id {id} does not exist",
        )
    return seller 


@router.get("/all_sellers", response_model=List[ShowSeller])
def read_sellers(db: Session = Depends(get_db)):
    sellers = list_sellers(db=db)
    return sellers


@router.put("/update_seller/{id}")
def update_seller(id: int, seller: SellerCreate, db: Session = Depends(get_db)):
    current_user = 1
    message = update_seller_by_id(id=id, seller=seller, db=db, owner_id=current_user)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Seller with id {id} not found"
        )
    return {"msg": "Successfully updated data."}


@router.delete("/delete_seller/{id}")
def delete_seller(
    id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_from_token),
):
    seller = retreive_seller(id=id, db=db)
    if not seller:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seller with id {id} does not exist",
        )
    print(seller.owner_id, current_user.id, current_user.is_superuser)
    if seller.owner_id == current_user.id or current_user.is_superuser:
        delete_seller_by_id(id=id, db=db, owner_id=current_user.id)
        return {"detail": "Successfully deleted."}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )


@router.get("/autocomplete_seller")
def autocomplete(term: Optional[str] = None, db: Session = Depends(get_db)):
    sellers = search_seller(term, db=db)
    seller_names = []
    for seller in sellers:
        seller_names.append(seller.name)
    return seller_names
