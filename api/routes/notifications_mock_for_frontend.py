from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from notification.line_bot_service import send_line_notification
from api.main import get_current_user # Ensure auth is used

router = APIRouter()

class LineMessageRequest(BaseModel):
    user_id: str
    message: str

@router.post("/notifications/send-line-message", status_code=status.HTTP_200_OK)
def send_line_message_mock(request: LineMessageRequest, current_user: dict = Depends(get_current_user)):
    """
    Mock endpoint for frontend to trigger LINE notifications.
    In a real app, specific business logic would trigger this, not direct frontend calls.
    """
    print(f"User {current_user['username']} (Tenant {current_user['tenant_id']}) requested LINE notification:")
    print(f"  To: {request.user_id}")
    print(f"  Message: {request.message}")
    
    # Actually attempt to send the LINE notification via the service
    success = send_line_notification(request.user_id, request.message)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send LINE notification")
    return {"message": "LINE notification mock sent successfully"}
