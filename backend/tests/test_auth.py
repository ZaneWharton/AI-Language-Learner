import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from app.models import Base
from app.db import get_db
import app.routes.auth as auth

#Create a fastapi instance for testing
test_app = FastAPI()
test_app.include_router(auth.router)
@test_app.get("/")
async def _root():
    return {"ok": True}

#Create in-memort SQLite engine and session
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
AsyncSessionLocalTest = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with AsyncSessionLocalTest() as session:
        yield session
test_app.dependency_overrides[get_db] = override_get_db

#Create tables before tests run
@pytest.fixture(scope="module", autouse=True)
def prepare_database():

    #Create tables
    async def _prep():
        async with engine_test.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.get_event_loop().run_until_complete(_prep())
    yield
    
    #Drop tables (cleanup)
    async def _drop():
        async with engine_test.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    asyncio.get_event_loop().run_until_complete(_drop())

#AsyncClient fixture
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://localhost", trust_env=False) as client:
        yield client

#Tests
@pytest.mark.asyncio
async def test_endpoints(async_client: AsyncClient):

    #Register
    resp = await async_client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "secret123"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert "id" in data

    #Duplicate register fails
    resp2 = await async_client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "secret123"}
    )
    assert resp2.status_code == 400

    #Login
    login_resp = await async_client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "secret123"}
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    #/me with access_token
    me_resp = await async_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "alice@example.com"

    #Refresh
    refresh_resp = await async_client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert refresh_resp.status_code == 200
    refresh_data = refresh_resp.json()
    assert "access_token" in refresh_data and "refresh_token" in refresh_data

@pytest.mark.asyncio
async def test_invalid_login(async_client: AsyncClient):

    #Login with non-existent user
    resp = await async_client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "nope"}
    )
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_me_unauthorized(async_client: AsyncClient):

    #Call /me with no token
    resp = await async_client.get("/auth/me")
    assert resp.status_code == 401

    #Call /me with an invalid token
    resp2 = await async_client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )

    assert resp2.status_code == 401