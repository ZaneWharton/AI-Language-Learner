from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.db import get_db
from app.models import User
from passlib.context import CryptContext 
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings

#Initialize API Router, hashing context, and oauth2 scheme
router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')

#Pydantic models for request and response validation

class CreateUserRequest(BaseModel):
    #Registration Input
    email: EmailStr
    password: str

class UserRead(BaseModel):
    #For returning user data
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode = True

class LoginRequest(BaseModel): 
    #Login input
    email: EmailStr
    password: str

class Token(BaseModel):
    #Access and refresh tokens
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

#JWT token creation and decoding helpers

def create_jwt_token(user_id: int):
    #Short lived access token, contains user id
    now = datetime.now(timezone.utc)
    encode = {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "type": "access"}
    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(user_id: int):
    #Long lived refresh token, contains user id
    now = datetime.now(timezone.utc)
    encode = {"sub": str(user_id), "iat": now, "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "type": "refresh"}
    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_jwt_token(token: str):
    #Decode and validate JWT token
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

#Auth routes

@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: CreateUserRequest, db: AsyncSession = Depends(get_db)):
    #Registers new user, hashes password and stores user info in database

    #User already exists
    existing = await db.execute(select(User).filter_by(email=data.email))
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    
    #Create user
    user = User(
        email = data.email,
        hashed_password = bcrypt_context.hash(data.password),
        created_at = datetime.now(timezone.utc)
    )
    
    #Persist in database
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    #Authenticate use and issue JWT tokens

    #Retrieve user
    result = await db.execute(select(User).filter_by(email=data.email))
    user = result.scalars().first()

    #Validate user
    if not user or not bcrypt_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.", headers={"WWW-Authenticate": "Bearer"})
    
    #Create JWT
    expires = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    access_token = create_jwt_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return Token(access_token=access_token, refresh_token=refresh_token, expires_in=expires)

@router.post("/refresh", response_model=Token)
async def refresh(token: str = Depends(oauth2_bearer)):
    #Refresh access token

    payload = decode_jwt_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.", headers={"WWW-Authenticate": "Bearer"})
    
    user_id = int(payload["sub"])
    expires = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    access_token = create_jwt_token(user_id)
    refresh_token = create_refresh_token(user_id)

    return Token(access_token=access_token, refresh_token=refresh_token, expires_in=expires)


async def get_current_user(token: str = Depends(oauth2_bearer), db: AsyncSession = Depends(get_db)) -> User:
    #Returns current authenticated user by decoding access token

    payload = decode_jwt_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.", headers={"WWW-Authenticate": "Bearer"})
    
    user_id = int(payload["sub"])
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.", headers={"WWW-Authenticate": "Bearer"})
    return user
    
@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)):
    #Gets the logged in user's details

    return current_user