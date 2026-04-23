from __future__ import annotations
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Base event
# ---------------------------------------------------------------------------
class ZaloBaseEvent(BaseModel):
    app_id: str
    timestamp: int  # milliseconds epoch


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------
class ZaloSender(BaseModel):
    id: str  # user id


class ZaloRecipient(BaseModel):
    id: str  # oa id


# ---------------------------------------------------------------------------
# Message payload variants
# ---------------------------------------------------------------------------
class ZaloTextMessage(BaseModel):
    msg_id: str
    text: str


class ZaloAttachmentPayloadImage(BaseModel):
    url: str
    thumbnail: str | None = None
    description: str | None = None


class ZaloCoordinates(BaseModel):
    latitude: float
    longitude: float


class ZaloAttachmentPayloadLocation(BaseModel):
    coordinates: ZaloCoordinates
    address: str | None = None
    name: str | None = None


# ---------------------------------------------------------------------------
# Attachment wrappers
# ---------------------------------------------------------------------------
class ZaloImageMessage(BaseModel):
    msg_id: str
    attachments: list[ZaloAttachmentPayloadImage]


class ZaloLocationMessage(BaseModel):
    msg_id: str
    attachments: list[ZaloAttachmentPayloadLocation]


# ---------------------------------------------------------------------------
# Concrete event models
# ---------------------------------------------------------------------------
class ZaloUserSendTextEvent(ZaloBaseEvent):
    event_name: Literal["user_send_text"]
    sender: ZaloSender
    recipient: ZaloRecipient
    message: ZaloTextMessage


class ZaloUserSendImageEvent(ZaloBaseEvent):
    event_name: Literal["user_send_image"]
    sender: ZaloSender
    recipient: ZaloRecipient
    message: ZaloImageMessage


class ZaloUserSendLocationEvent(ZaloBaseEvent):
    event_name: Literal["user_send_location"]
    sender: ZaloSender
    recipient: ZaloRecipient
    message: ZaloLocationMessage


# ---------------------------------------------------------------------------
# Union type + discriminated parsing
# ---------------------------------------------------------------------------
ZaloWebhookPayload = Annotated[
    Union[ZaloUserSendTextEvent, ZaloUserSendImageEvent, ZaloUserSendLocationEvent],
    Field(discriminator="event_name"),
]
