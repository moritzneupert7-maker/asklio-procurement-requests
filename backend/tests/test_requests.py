from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from decimal import Decimal

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
                "description": "Adobe Photoshop CC 2024 - 1 Year Subscription License with cloud storage",
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
    assert "2024" in data["order_lines"][0]["description"]

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


def test_create_from_offer():
    """Uploading an offer file creates a request with extracted data and correct defaults."""
    from app.services.extractor import OfferExtraction, ExtractedOrderLine

    mock_extraction = OfferExtraction(
        title="Office Supplies Purchase",
        vendor_name="ACME Corp",
        vendor_vat_id="DE123456789",
        department=None,
        order_lines=[
            ExtractedOrderLine(
                description="Printer paper A4",
                unit_price=Decimal("9.99"),
                amount=100,
                unit="packs",
                total_price=Decimal("999.00"),
            ),
        ],
        total_cost=Decimal("999.00"),
    )

    with patch("app.routers.requests.extract_offer_text", return_value=mock_extraction), \
         patch("app.routers.requests.predict_commodity_group_id", return_value="999"):
        offer_content = b"Offer from ACME Corp\nPrinter paper A4, 100 packs @ 9.99 each"
        r = client.post(
            "/requests/create-from-offer",
            files={"file": ("offer.txt", offer_content, "text/plain")},
        )

    assert r.status_code == 200
    data = r.json()
    assert data["requestor_name"] == "Moritz Neupert"
    assert data["department"] == "Marketing"
    assert data["title"] == "Office Supplies Purchase"
    assert data["vendor_name"] == "ACME Corp"
    assert data["vendor_vat_id"] == "DE123456789"
    assert data["current_status"] == "Open"
    assert len(data["order_lines"]) == 1
    assert data["order_lines"][0]["description"] == "Printer paper A4"
    assert float(data["total_cost"]) == 999.00


def test_create_from_offer_uses_extracted_department():
    """When the offer contains a department, it is used instead of the default."""
    from app.services.extractor import OfferExtraction, ExtractedOrderLine

    mock_extraction = OfferExtraction(
        title="IT Equipment",
        vendor_name="TechVendor",
        vendor_vat_id=None,
        department="Engineering",
        order_lines=[
            ExtractedOrderLine(
                description="Monitor",
                unit_price=Decimal("300.00"),
                amount=2,
                unit="pcs",
                total_price=Decimal("600.00"),
            ),
        ],
        total_cost=Decimal("600.00"),
    )

    with patch("app.routers.requests.extract_offer_text", return_value=mock_extraction), \
         patch("app.routers.requests.predict_commodity_group_id", return_value="999"):
        r = client.post(
            "/requests/create-from-offer",
            files={"file": ("offer.txt", b"test content", "text/plain")},
        )

    assert r.status_code == 200
    data = r.json()
    assert data["department"] == "Engineering"


def test_create_from_offer_unsupported_file_type():
    """Uploading an unsupported file type returns 400."""
    r = client.post(
        "/requests/create-from-offer",
        files={"file": ("offer.docx", b"test", "application/octet-stream")},
    )
    assert r.status_code == 400
    assert "Supported offer types" in r.json()["detail"]
