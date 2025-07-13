from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://admin:password@db:5432/language_learner"

#Create async engine (Connection pool and Driver)
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

#Session factory bound to engine
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

