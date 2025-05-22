import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.anyio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:   
        response = await ac.post("/api/auth/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "TestPassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        response = await ac.post("/api/auth/login", json={
            "email": "testuser@example.com",
            "password": "TestPassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data