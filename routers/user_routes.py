from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from auth_utils import get_password_hash, verify_password, create_access_token, decode_token
from mongo_conn import db 

router = APIRouter()

class CreateUser(BaseModel):
    email: str
    password: str

@router.post("/register",)
async def create_user(user: CreateUser):
    existing_user = db.user.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    encripted_password = get_password_hash(user.password)
    db.user.insert_one({"email": user.email, "password": encripted_password})
    return {"message": "User created successfully"}

class LoginUser(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(user: LoginUser):
    existing_user = db.user.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    access_token = create_access_token(data={"id": str(existing_user["_id"])})
    return {"access_token": access_token}