from fastapi import APIRouter, Form, File, UploadFile, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
from db.database import SessionLocal
from app.models import User, QRCode, History
from fastapi.templating import Jinja2Templates
import httpx


templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.post("/generate_qr")
async def generate_qr(request: Request, qr_data: str = Form(...)):
    
    url = f"https://api.qrserver.com/v1/create-qr-code/?data={qr_data}&size=150x150"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return JSONResponse(content={"error": "QR API failed"}, status_code=500)
    
    db = SessionLocal()
    username = request.session.get("username")
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "You are not logged in"})  
    
    qr_record = QRCode(user_id=user.id, content=qr_data)
    
    db.add(qr_record)
    db.commit()
    db.refresh(qr_record)
    
    history_record = History(user_id=user.id, qrcode_id=qr_record.id, qrcode_content=qr_data, action_type="generate")
    
    db.add(history_record)
    db.commit()
    db.refresh(history_record)
    db.close()
    
    return StreamingResponse(BytesIO(response.content), media_type="image/png")


@router.post("/scan_qr")
async def scan_qr(request: Request, file: UploadFile = File(...)):
    try:
        img_data = await file.read()
        img = Image.open(BytesIO(img_data))
        
        decoded_objects = decode(img)
        
        if not decoded_objects:
            return JSONResponse({"error": "No QR code found in the image"}, status_code=400)
        
        decoded_data = decoded_objects[0].data.decode("utf-8")
        
        db = SessionLocal()
        username = request.session.get("username")
        
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "You are not logged in"})
            
        history_record = History(user_id=user.id, qrcode_id=None, qrcode_content=decoded_data, action_type="scan")
        
        db.add(history_record)
        db.commit()
        db.refresh(history_record)
        db.close()
        
        return JSONResponse({"decoded_data": decoded_data})
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/scan_qr_camera")
async def scan_qr_text(request: Request):
    body = await request.json()
    qr_data = body.get("qr_data")
    
    if not qr_data:
        return JSONResponse({"error": "No QR data"}, status_code=400)
    
    db = SessionLocal()
    username = request.session.get("username")

    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    history_record = History(user_id=user.id, qrcode_id=None, qrcode_content=qr_data, action_type="scan")

    db.add(history_record)
    db.commit()
    db.refresh(history_record)
    db.close()

    return JSONResponse({"decoded_data": qr_data})