from apis.version1.route_login import login_for_access_token
from db.session import get_db
from core.security import get_api_key_default, API_KEY_NAME
from fastapi import APIRouter, Security, Depends, FastAPI, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse

from webapps.auth.forms import LoginForm

from db.repository.books import list_books
from db.session import get_db



templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/login/")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login/", tags=["login"])
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successful :)")
            response = templates.TemplateResponse("auth/login.html", form.__dict__)
            response = templates.TemplateResponse("general_pages/homepage.html", form.__dict__)
            login_for_access_token(response=response, form_data=form, db=db)
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("auth/login.html", form.__dict__)
    return templates.TemplateResponse("auth/login.html", form.__dict__)


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db), msg: str = None, api_key: APIKey = Depends(get_api_key_default)):
    if (api_key is None):
        #raise HTTPException(
        #    status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        #)
        return RedirectResponse(url="/login/")
    else:
        books = list_books(db=db)
        return templates.TemplateResponse(
            "general_pages/homepage.html", {"request": request, "books": books, "msg": msg}
        )

@router.get("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/login/")
    response.delete_cookie(API_KEY_NAME)
    return response
