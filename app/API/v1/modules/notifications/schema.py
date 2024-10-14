from pydantic import Field
from typing import Optional, List

from ...helpers.schema import Base


class NotificationTypeItem(Base):
    name: str

class SeenByItem(Base):
    id: int
    user_id: int = Field(..., alias="userId")
    notification_id: int = Field(..., alias="notificationId")

class NotificationItem(Base):
    id: int
    message: str
    is_read: bool = Field(..., alias="isRead")
    case_id: Optional[int] = Field(None, alias="caseId")
    quote_id: Optional[int] = Field(None, alias="quoteId")
    notification_type: Optional[NotificationTypeItem] = Field(None, alias="type")
    seen_by: List[SeenByItem] = Field(default_factory=list, alias="seenBy")


    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "message": "New quote created",
                "isRead": False,
                "caseId": 1,
                "type": "SYSTEM_ALERT",

            }
        }

class ToReadNotification(Base):
    id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
            }
        }

        