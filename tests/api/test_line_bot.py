import pytest
from fastapi.testclient import TestClient
from api.main import app, create_access_token, settings
from datetime import timedelta
import os
import json
import hmac
import hashlib
import base64

# Mock the LineBotApi and WebhookHandler to prevent actual API calls during tests
class MockLineBotApi:
    def __init__(self, token):
        self.token = token
    def push_message(self, user_id, message):
        print(f"MockLineBotApi: Pushed message '{message.text}' to {user_id}")
        return True
    def reply_message(self, reply_token, message):
        print(f"MockLineBotApi: Replied to {reply_token} with '{message.text}'")
        return True

class MockWebhookHandler:
    def __init__(self, secret):
        self.secret = secret
        self.added_handlers = []

    def add(self, event_type, message_type):
        def decorator(func):
            self.added_handlers.append(func)
            return func
        return decorator

    def handle(self, body, signature):
        # Simulate LINE's signature validation logic
        hash = hmac.new(self.secret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
        computed_signature = base64.b64encode(hash).decode('utf-8')
        
        if signature != computed_signature:
            raise InvalidSignatureError("Invalid signature mock")
        
        # Simulate handling a text message event
        event_data = json.loads(body)
        if event_data.get("events") and event_data["events"][0]["type"] == "message":
            mock_event = type('obj', (object,), {
                'reply_token': 'mock_reply_token',
                'message': type('obj', (object,), {'type': 'text', 'text': event_data["events"][0]["message"]["text"]})
            })()
            for handler_func in self.added_handlers:
                try:
                    handler_func(mock_event)
                except Exception as e:
                    print(f"Mock handler error: {e}")
            return True
        return False

# Override LineBotApi and WebhookHandler in the notification module
@pytest.fixture(autouse=True)
def mock_line_bot_modules(monkeypatch):
    mock_channel_access_token = "mock_access_token_123"
    mock_channel_secret = "mock_secret_abc"
    mock_user_id = "U1234567890abcdef1234567890abcdef" # A valid-looking LINE user ID
    
    monkeypatch.setattr("notification.line_bot_service.LineBotApi", MockLineBotApi)
    monkeypatch.setattr("notification.line_bot_service.WebhookHandler", MockWebhookHandler)
    
    monkeypatch.setenv("LINE_CHANNEL_ACCESS_TOKEN", mock_channel_access_token)
    monkeypatch.setenv("LINE_CHANNEL_SECRET", mock_channel_secret)
    monkeypatch.setenv("LINE_USER_ID", mock_user_id) # Set a mock user ID for push messages
    
    # Re-initialize the LineBotApi and handler within the module scope for the test
    # This is a bit of a hack; in a larger app, DI would handle this.
    monkeypatch.setattr("notification.line_bot_service.line_bot_api", MockLineBotApi(mock_channel_access_token))
    monkeypatch.setattr("notification.line_bot_service.handler", MockWebhookHandler(mock_channel_secret))


client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    token = create_access_token(data={"sub": "testuser", "tenant_id": 1}, expires_delta=timedelta(minutes=60))
    return {"Authorization": f"Bearer {token}"}

def test_send_line_message_mock_endpoint(auth_headers, capsys):
    user_id = os.getenv("LINE_USER_ID")
    message_text = "Test message from API"
    response = client.post(
        "/api/v1/notifications/send-line-message",
        json={"user_id": user_id, "message": message_text},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "LINE notification mock sent successfully"
    
    captured = capsys.readouterr()
    assert f"MockLineBotApi: Pushed message '{message_text}' to {user_id}" in captured.out

def test_line_webhook_valid_signature_and_message(capsys):
    mock_channel_secret = os.getenv("LINE_CHANNEL_SECRET")
    mock_body_str = json.dumps({"events": [{"type": "message", "message": {"type": "text", "text": "Hello LINE"}}]}, ensure_ascii=False)
    
    # Manually compute a valid signature for the mock body
    hash = hmac.new(mock_channel_secret.encode('utf-8'), mock_body_str.encode('utf-8'), hashlib.sha256).digest()
    valid_signature = base64.b64encode(hash).decode('utf-8')

    response = client.post(
        "/api/v1/line-webhook",
        headers={"X-Line-Signature": valid_signature, "Content-Type": "application/json"},
        content=mock_body_str.encode('utf-8')
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    captured = capsys.readouterr()
    assert "MockLineBotApi: Replied to mock_reply_token with '您好！我們已收到您的訊息：'Hello LINE'。謝謝您的回覆！'" in captured.out

def test_line_webhook_invalid_signature():
    mock_body = json.dumps({"events": []}, ensure_ascii=False)
    response = client.post(
        "/api/v1/line-webhook",
        headers={"X-Line-Signature": "invalid-signature", "Content-Type": "application/json"},
        content=mock_body.encode('utf-8')
    )
    assert response.status_code == 400
    assert "Invalid signature" in response.json()["detail"] # Should catch InvalidSignatureError
