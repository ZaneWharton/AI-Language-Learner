from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db import get_db
import app.routes.auth as auth


app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)

@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    #Health check endpoint, verifies the app connects to the Postgres instance
    
    await db.execute(text("SELECT 1"))
    return {"status" : "OK"}