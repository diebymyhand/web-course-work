from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from db.database import SessionLocal
from app.models import User
from sqlalchemy import and_


templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.post("/register")
async def register_user(request: Request, 
                        username: str = Form(...), 
                        password: str = Form(...), 
                        repeat_password: str = Form(...)):
    
    if password != repeat_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match"})

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    
    if user:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "error": "Username already taken"})
    
    new_user = User(username = username, password = password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    request.session["username"] = new_user.username
    return RedirectResponse("/home", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/login")
async def login_user(request: Request,
                     username: str = Form(...),
                     password: str = Form(...)):
    
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Username not found"})    
    elif user.password != password:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Wrong password"
        })
        
    request.session["username"] = user.username
    return RedirectResponse("/home", status_code=status.HTTP_303_SEE_OTHER)
    
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)