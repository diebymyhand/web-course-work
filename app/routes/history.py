from fastapi import APIRouter, Request
from app.models import User, History
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db.database import SessionLocal

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/history", response_class=HTMLResponse)
async def show_history(request: Request):
    db = SessionLocal()
    
    username = request.session.get("username")
    if not username:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Please log in first."})
    
    user = db.query(User).filter(User.username == username).first()
    actions = db.query(History).filter(History.user_id == user.id).order_by(History.timestamp.desc()).all()

    return templates.TemplateResponse("history.html", {
        "request": request,
        "username": username,
        "actions": actions
    })