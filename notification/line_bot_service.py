from fastapi import APIRouter, HTTPException, Request, Header
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextMessage, MessageEvent
import os
import hmac
import hashlib
import base64

router = APIRouter()

# Get LINE channel access token and secret from environment variables
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Initialize LineBotApi and WebhookHandler only if credentials are provided
if LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET and \
   "your_line_channel_access_token" not in LINE_CHANNEL_ACCESS_TOKEN and \
   "your_line_channel_secret" not in LINE_CHANNEL_SECRET:
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(LINE_CHANNEL_SECRET)
    print("LINE Bot API and Handler initialized.")
else:
    line_bot_api = None
    handler = None
    print("LINE Bot API and Handler not initialized. Please set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET in .env.")


def send_line_notification(user_id: str, message: str):
    """Send a push message to a specific LINE user."""
    if not line_bot_api:
        print("LINE Bot API not initialized. Cannot send notification.")
        return False

    try:
        # Check if user_id is a valid LINE user ID format (starts with U) and not the mock default
        if not user_id or not user_id.startswith('U') or user_id == "Udeadbeefdeadbeefdeadbeefdeadbeef":
            print(f"WARNING: Invalid LINE_USER_ID '{user_id}'. Please set a real LINE user ID for actual notifications.")
            return False
            
        line_bot_api.push_message(user_id, TextMessage(text=message))
        print(f"LINE notification sent to {user_id}: {message}")
        return True
    except Exception as e:
        print(f"Failed to send LINE notification: {e}")
        return False

@router.post("/line-webhook")
async def line_webhook(request: Request, x_line_signature: str = Header(None)):
    """Handle incoming LINE webhook events and validate signature."""
    if not handler:
        raise HTTPException(status_code=503, detail="LINE Webhook handler not initialized. Check server configuration.")

    body = await request.body()
    try:
        handler.handle(body.decode('utf-8'), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature. Please check your channel secret.")
    except Exception as e:
        print(f"Error handling LINE webhook event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error handling webhook.")
    
    print("Received and handled LINE webhook event.")
    return {"status": "ok"}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """Example handler for text messages from users."""
    reply_message = f"您好！我們已收到您的訊息：'{event.message.text}'。謝謝您的回覆！"
    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_message))

if __name__ == "__main__":
    # Example usage
    mock_user_id = os.getenv("LINE_USER_ID", "mock_user_id")
    send_line_notification(mock_user_id, "恭喜！您的訂單 #123456 已成功出貨。")
