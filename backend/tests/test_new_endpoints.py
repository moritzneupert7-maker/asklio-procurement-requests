from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)


def test_predict_commodity_group():
    """Test the predict commodity group endpoint."""
    # Mock the OpenAI client
    with patch('app.services.commodity.client') as mock_client:
        # Create a mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.parsed = MagicMock()
        mock_response.choices[0].message.parsed.commodity_group_id = "029"
        mock_response.choices[0].message.refusal = None
        
        mock_client.chat.completions.parse.return_value = mock_response
        
        # Test the endpoint
        response = client.post(
            "/requests/predict-commodity-group",
            json={"title": "New laptop for development"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "commodity_group_id" in data
        assert data["commodity_group_id"] == "029"


def test_delete_all_requests():
    """Test the delete all requests endpoint."""
    # First create some requests
    payload = {
        "requestor_name": "Test User",
        "title": "Test Request",
        "department": "IT",
        "vendor_name": "Test Vendor",
        "order_lines": [
            {"description": "Test Item", "unit_price": 100, "amount": 1}
        ],
    }
    client.post("/requests", json=payload)
    
    # Verify we have requests
    requests = client.get("/requests").json()
    initial_count = len(requests)
    assert initial_count > 0
    
    # Delete all requests
    response = client.delete("/requests")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    
    # Verify all requests are gone
    requests_after = client.get("/requests").json()
    assert len(requests_after) == 0


def test_chat_endpoint():
    """Test the chat endpoint."""
    # Mock the OpenAI client
    with patch('app.routers.chat.client') as mock_client:
        # Create a mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello! I'm AskLio, how can I help you?"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test the endpoint
        response = client.post(
            "/chat",
            json={"message": "Hello"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "AskLio" in data["reply"]


def test_chat_endpoint_no_api_key():
    """Test the chat endpoint when OpenAI is not configured."""
    with patch('app.routers.chat.client', None):
        response = client.post(
            "/chat",
            json={"message": "Hello"}
        )
        
        assert response.status_code == 503
