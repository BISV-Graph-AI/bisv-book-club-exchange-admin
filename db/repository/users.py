from core.hashing import Hasher
from db.models.users import Users
from schemas.users import UserCreate
from sqlalchemy.orm import Session


def create_new_user(user: UserCreate, db: Session):
    user = Users(
        username=user.username,
        email=user.email,
        hashed_password=Hasher.get_password_hash(user.password),
        otp_secret=user.otp_secret,
        is_active=False,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(email: str, db: Session):
    user = db.query(Users).filter(Users.email == email).first()
    return user


def update_user_username_by_email(email: str, username: str, db: Session):
    user = get_user_by_email(email=email, db=db)
    if not user:
        return 0
    user.username = username 
    db.commit()
    db.refresh(user)
    return 1


def update_user_password_by_email(email: str, password: str, db: Session):
    user = get_user_by_email(email=email, db=db)
    if not user:
        return 0
    user.hashed_password = Hasher.get_password_hash(password) 
    db.commit()
    db.refresh(user)
    return 1

def update_user_otp_secret_by_email(email: str, otp_secret: str, db: Session):
    user = get_user_by_email(email=email, db=db)
    if not user:
        return 0
    user.otp_secret = otp_secret
    db.commit()
    db.refresh(user)
    return 1

def update_user_is_active_by_email(email: str, is_active: bool, db: Session):
    user = get_user_by_email(email=email, db=db)
    if not user:
        return 0
    user.is_active = is_active 
    #user.update(user.__dict__)
    db.commit()
    db.refresh(user)
    return 1
