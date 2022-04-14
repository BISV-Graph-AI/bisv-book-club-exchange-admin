from db.models.sellers import Sellers
from schemas.sellers import SellerCreate
from sqlalchemy.orm import Session


def create_new_seller(seller: SellerCreate, db: Session, owner_id: int):
    seller_object = Sellers(**seller.dict(), owner_id=owner_id)
    db.add(seller_object)
    db.commit()
    db.refresh(seller_object)
    return seller_object


def retreive_seller(id: int, db: Session):
    item = db.query(Sellers).filter(Sellers.id == id).first()
    return item


def get_seller_id_from_collection(collection: str, db: Session):
    item = db.query(Sellers).filter(Sellers.collection == collection)
    return item


def list_sellers(db: Session):
    sellers = db.query(Sellers).all()
    return sellers


def update_seller_by_id(id: int, seller: SellerCreate, db: Session, owner_id):
    existing_seller = db.query(Sellers).filter(Sellers.id == id)
    if not existing_seller.first():
        return 0
    seller.__dict__.update(
        owner_id=owner_id
    )  # update dictionary with new key value of owner_id
    existing_seller.update(seller.__dict__)
    db.commit()
    return 1


def delete_seller_by_id(id: int, db: Session, owner_id):
    existing_seller = db.query(Sellers).filter(Sellers.id == id)
    if not existing_seller.first():
        return 0
    existing_seller.delete(synchronize_session=False)
    db.commit()
    return 1


def search_seller(query: str, db: Session):
    sellers = db.query(Sellers).filter(Sellers.title.contains(query))
    return sellers
