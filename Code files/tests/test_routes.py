def test_public_pages(client):
    for path in ["/","/login","/register","/testimonials","/health","/startup"]:
        assert client.get(path).status_code==200

def test_history(auth_client):
    r=auth_client.get("/history")
    assert r.status_code==200 and isinstance(r.json(),list)
