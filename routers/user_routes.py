from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from auth_utils import get_password_hash, verify_password, create_access_token, decode_token
from mongo_conn import db 

router = APIRouter()

class CreateUser(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="strongpassword")

@router.post(
    "/register",
    summary="Register a new user",
    description="Register a new user with an email and password.",
    response_description="The user has been created successfully.",
    responses={
        400: {"description": "User already exists"}
    }
)
async def create_user(user: CreateUser):
    existing_user = db.user.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    encripted_password = get_password_hash(user.password)
    db.user.insert_one({"email": user.email, "password": encripted_password})
    return {"message": "User created successfully"}

class LoginUser(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="strongpassword")

@router.post(
    "/login",
    summary="Login a user",
    description="Login a user with an email and password.",
    response_description="The access token for the user.",
    responses={
        400: {"description": "User not found or invalid password"}
    }
)
async def login(user: LoginUser):
    existing_user = db.user.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    access_token = create_access_token(data={"id": str(existing_user["_id"])})
    return {"access_token": access_token}