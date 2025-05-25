from fastapi import FastAPI, Request
from app.routes import qr, auth, history
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(SessionMiddleware, secret_key="super_secret_key")

@app.get("/")
async def login_user(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def main_html(request: Request):
    username = request.session.get("username")
    if not username:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Please log in first."})
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

@app.get("/register", response_class=HTMLResponse)
async def register_user(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


app.include_router(auth.router)
app.include_router(qr.router)
app.include_router(history.router)