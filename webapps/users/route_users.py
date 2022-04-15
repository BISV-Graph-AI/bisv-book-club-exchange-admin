from app import *
from db.repository.users import create_new_user
from db.repository.users import get_user_by_email
from db.repository.users import update_user_username_by_email
from db.repository.users import update_user_password_by_email
from db.repository.users import update_user_otp_secret_by_email
from db.repository.users import update_user_is_active_by_email
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import responses
from fastapi import status
from fastapi.templating import Jinja2Templates
from schemas.users import UserCreate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from webapps.users.forms import UserCreateForm

import os
import pyotp
import secrets


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)

ALLOWED_EMAIL_LIST = os.getenv('ALLOWED_EMAIL_LIST').split(',')


def create_temp_user(email, temp_password, otp_secret, db):
    user = None
    try:
        user = get_user_by_email(email=email, db=db)
        if (not user):
            usercreate = UserCreate(
                username='firsttimeusername', email=email, password=temp_password, otp_secret=otp_secret, is_active=False
            )
            user = create_new_user(user=usercreate, db=db)
    except Exception:
        user = None
    return user


@router.get("/register/")
def register(request: Request):
    return templates.TemplateResponse("users/preregister.html", {"request": request})


@router.post("/register/")
async def register(request: Request, db: Session = Depends(get_db)):
    form = UserCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            print(form.__dict__)
            user = get_user_by_email(email=form.email, db=db)
            is_active = False
            if (user):
                is_active = user.is_active
            if (form.email not in ALLOWED_EMAIL_LIST):
                form.__dict__.get("errors").append("Email: {} Is Not Allowed To Register.".format(form.email))
                return templates.TemplateResponse("users/preregister.html", form.__dict__)
            elif (is_active):
                form.__dict__.get("errors").append("Email: {} Exists.".format(form.email))
                return templates.TemplateResponse("users/preregister.html", form.__dict__)
            else:
                if (form.__dict__.get("otp_secret") is None):
                    print('111111111')
                    form.__dict__["otp_secret"] = "Please Enter the One-Time Password Sent to Your Email (Might be in the spam folder)."

                    # Create temp password and One-Time Password
                    password_length = 13
                    temp_password = secrets.token_urlsafe(password_length)
                    print(temp_password)
                    otp_secret = pyotp.random_base32()
                    print('22222222222')
                    print(otp_secret)

                    # Create temp user
                    email = form.__dict__.get("email")
                    print('EMAI ' + email)
                    user = create_temp_user(email, temp_password, otp_secret, db)
                    print('PPPPPPPPPPP')
                    if (user is not None):
                        form_username = form.__dict__.get("username")
                        form_password = form.__dict__.get("password")

                        print('333333333333')
                        if (form_username is None and form_password is None):
                            print('SEND EAMIL')
                            send_email(email, 'One-Time Password for BISV Book Exchange Club', 'Hello, \rYour One-Time Password Is: {}'.format(otp_secret))
                            update_user_otp_secret_by_email(email=email, otp_secret=otp_secret, db=db)
                            return templates.TemplateResponse("users/verification.html", form.__dict__)
                        else:
                            print('UPDATE PASS')
                            update_user_password_by_email(email=email, password=form_password, db=db)
                            update_user_is_active_by_email(email=email, is_active=True, db=db)
                            return templates.TemplateResponse("auth/login.html", form.__dict__)
                    else:
                        form.__dict__.get("errors").append("There is an issue registering. Please try it again")
                        return templates.TemplateResponse("users/preregister.html", form.__dict__)
                else:
                    print('444444444444')
                    email = form.__dict__.get("email")
                    username = form.__dict__.get("username")
                    otp_secret = form.__dict__.get("otp_secret")
                    password = form.__dict__.get("password")
                    print(form.__dict__)
                    print('-----------')
                    if (otp_secret == user.otp_secret):
                        if (user.username == "firsttimeusername"):
                            print('===========UUUUU ')
                            if (username is None):
                                username = user.email.split('@')[0] 
                            update_user_username_by_email(email=email, username=username, db=db)
                        if (username is None):
                            print('username NONE')
                        else:
                            print('username ' + str(username))
                        if (password is None):
                            print('password NONE')
                        else:
                            print('password ' + str(password))

                        if (password is None):
                            print('TO REGISTER')
                            form.__dict__["username"] = username
                            form.__dict__["email"] = user.email
                            return templates.TemplateResponse("users/register.html", form.__dict__)
                        else:
                            print('TO LOGIN')
                            update_user_password_by_email(email=email, password=password, db=db)
                            update_user_is_active_by_email(email=email, is_active=True, db=db)
                            return responses.RedirectResponse(
                                f"/login/", status_code=status.HTTP_302_FOUND
                            )
                    else:
                        print('EEEEEEEEEEEE')
                        form.__dict__["otp_secret"] = "Verification Failed. Please Try It Again."
                        return templates.TemplateResponse("users/verification.html", form.__dict__)
        except Exception as err:
            form.__dict__.get("errors").append('Exception: {}'.format(str(err)))
            return templates.TemplateResponse("users/preregister.html", form.__dict__)

    return templates.TemplateResponse("users/preregister.html", form.__dict__)

