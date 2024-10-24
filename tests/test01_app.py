import pytest
from fastapi.testclient import TestClient
from main import app
import sys
import os
from pathlib import Path
client = TestClient(app)

sys.path.append(str(Path(__file__).resolve().parent.parent))
# Testes para o endpoint /register e login

def test_register_user():
    response = client.post("/register", json={"email": "test4@example.com", "password": "securepassword"})
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}

    # Tentar registrar o mesmo usuário novamente
    response = client.post("/register", json={"email": "test4@example.com", "password": "securepassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}
from datetime import datetime, timedelta, timezone
    
def test_login_user():
    # Registrar um usuário antes de tentar o login
    client.post("/register", json={"email": "test4@example.com", "password": "securepassword"})

    # Tentar fazer login com credenciais corretas
    response = client.post("/login", json={"email": "test4@example.com", "password": "securepassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Tentar fazer login com senha errada
    response = client.post("/login", json={"email": "test4@example.com", "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid password"}

    # Tentar fazer login com um usuário não registrado
    response = client.post("/login", json={"email": "notfound@example.com", "password": "securepassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "User not found"}