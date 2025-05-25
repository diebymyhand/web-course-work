from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    qrcodes = relationship("QRCode", back_populates="user") 
    actions = relationship("History", back_populates="user")

class QRCode(Base):
    __tablename__ = "qrcodes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="qrcodes")
    actions = relationship("History", back_populates="qrcode")

class History(Base):
    __tablename__ = "history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    qrcode_id = Column(Integer, ForeignKey("qrcodes.id"))
    qrcode_content = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    action_type = Column(String)
    
    user = relationship("User", back_populates="actions")  
    qrcode = relationship("QRCode", back_populates="actions") 

