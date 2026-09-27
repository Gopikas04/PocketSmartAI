def test_home_planner_fallback(auth_client):
    r=auth_client.post("/generate-home",json={"budget":50000,"style":"Modern","rooms":[{"room":"Living Room","item":"Ceiling fan","quantity":2}],"notes":""})
    assert r.status_code==200 and r.json()["planner_type"]=="home"

def test_party_planner_fallback(auth_client):
    r=auth_client.post("/generate-party",json={"budget":75000,"guests":50,"event_type":"Birthday","venue_details":"","location":"Chennai","food_preference":"Mixed","notes":""})
    assert r.status_code==200 and r.json()["planner_type"]=="party"

def test_jewelry_planner_fallback(auth_client):
    r=auth_client.post("/generate-jewelry",data={"budget":"15000","occasion":"Wedding","style":"Elegant","outfit_description":"Blue saree","notes":""})
    assert r.status_code==200 and r.json()["planner_type"]=="jewelry"
