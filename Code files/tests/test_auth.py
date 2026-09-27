def test_register_and_login(client):
    r=client.post("/register",json={"name":"Alice","email":"alice@example.com","password":"password123"})
    assert r.status_code==201
    r=client.post("/login",json={"email":"alice@example.com","password":"password123"})
    assert r.status_code==200
    assert "access_token" in r.cookies

def test_protected_session_requires_auth(client):
    assert client.get("/session-info").status_code==401
