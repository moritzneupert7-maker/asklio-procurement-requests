from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)  # TestClient lets you test without running uvicorn [web:345]

def test_create_request():
    payload = {
        "requestor_name": "John Doe",
        "title": "Adobe Creative Cloud Subscription",
        "department": "Creative Marketing Department",
        "vendor_name": "Global Tech Solutions",
        "vendor_vat_id": "DE987654321",
        "order_lines": [
            {
                "product": "Adobe Photoshop License",
                "description": "Adobe Photoshop License",
                "unit_price": 150,
                "amount": 10,
                "unit": "licenses"
            },
        ],
    }
    r = client.post("/requests", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert data["current_status"] == "Open"
    assert len(data["order_lines"]) == 1
    assert data["order_lines"][0]["product"] == "Adobe Photoshop License"

def test_status_change_creates_history():
    payload = {
        "requestor_name": "Jane Doe",
        "title": "Laptop Purchase",
        "department": "IT",
        "vendor_name": "Vendor X",
        "vendor_vat_id": None,
        "order_lines": [
            {"description": "Laptop", "unit_price": 1000, "amount": 1, "unit": "pcs"},
        ],
    }
    created = client.post("/requests", json=payload).json()
    rid = created["id"]

    updated = client.post(f"/requests/{rid}/status", json={"to_status": "In Progress", "changed_by": "Procurement"}).json()
    assert updated["current_status"] == "In Progress"
    assert len(updated["status_events"]) >= 2
