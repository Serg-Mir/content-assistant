import pytest
from unittest.mock import patch
from content_assistant.main import create_app
from fastapi.testclient import TestClient

app = create_app()
client = TestClient(app)


@pytest.mark.asyncio
@patch("content_assistant.routers.collections.generate_text")
async def test_integration_trigger_generate_text(mock_trigger_generate_text):
    mock_trigger_generate_text.return_value = "Generated test content in UTF16 format."

    request_data = {
        "keywords": ["test"],
        "domain": "test_domain",
        "word_count": 100,
        "audience": "test_audience",
        "tone": "test_tone"
    }
    response = client.post("/collections/generate_text", json=request_data)

    assert response.status_code == 200
    assert response.json()["generated_text"] == "Generated test content in UTF16 format."
