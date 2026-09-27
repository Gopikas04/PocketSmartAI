import os
from pathlib import Path
import tempfile
os.environ["DATABASE_URL"]=f"sqlite:///{Path(tempfile.gettempdir())/'pocketsmart_test.db'}"
os.environ["SECRET_KEY"]="test-secret-key"
os.environ["GEMINI_API_KEY"]=""
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base,engine
import pytest
@pytest.fixture(scope="session",autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine);Base.metadata.create_all(bind=engine);yield;Base.metadata.drop_all(bind=engine)
@pytest.fixture
def client():
    with TestClient(app) as c: yield c
@pytest.fixture
def auth_client(client):
    client.post("/register",json={"name":"Test User","email":"test@example.com","password":"password123"})
    client.post("/login",json={"email":"test@example.com","password":"password123"})
    return client
