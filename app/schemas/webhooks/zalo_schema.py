from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class ZaloModel(BaseModel):
    """Base for Zalo webhook DTOs: reject unknown fields at parse time."""

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Base event
# ---------------------------------------------------------------------------
class ZaloBaseEvent(ZaloModel):
    app_id: str
    timestamp: int  # milliseconds epoch


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------
class ZaloSender(ZaloModel):
    id: str  # user id


class ZaloRecipient(ZaloModel):
    id: str  # oa id


# ---------------------------------------------------------------------------
# Message payload variants
# ---------------------------------------------------------------------------
class ZaloTextMessage(ZaloModel):
    msg_id: str
    text: str


class ZaloAttachmentPayloadImage(ZaloModel):
    url: str
    thumbnail: str | None = None
    description: str | None = None


class ZaloCoordinates(ZaloModel):
    latitude: float
    longitude: float


class ZaloAttachmentPayloadLocation(ZaloModel):
    coordinates: ZaloCoordinates
    address: str | None = None
    name: str | None = None


# ---------------------------------------------------------------------------
# Attachment wrappers
# ---------------------------------------------------------------------------
class ZaloImageMessage(ZaloModel):
    msg_id: str
    attachments: list[ZaloAttachmentPayloadImage]


class ZaloLocationMessage(ZaloModel):
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

zalo_webhook_payload_adapter = TypeAdapter(ZaloWebhookPayload)


def parse_zalo_webhook_payload(data: object) -> ZaloUserSendTextEvent | ZaloUserSendImageEvent | ZaloUserSendLocationEvent:
    """Validate a decoded JSON body as ``ZaloWebhookPayload`` (discriminated union)."""
    return zalo_webhook_payload_adapter.validate_python(data)
