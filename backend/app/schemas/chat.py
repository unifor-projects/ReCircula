from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.usuario import UsuarioPublico


class ChatConversationCreate(BaseModel):
    user_id: int = Field(..., description="ID do outro usuário para conversa direta")


class ChatParticipantResponse(BaseModel):
    id: int
    user_id: int
    joined_at: datetime
    last_read_at: Optional[datetime] = None
    user: UsuarioPublico

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    created_at: datetime
    sender: UsuarioPublico

    model_config = {"from_attributes": True}


class ChatConversationResponse(BaseModel):
    id: int
    type: str
    name: Optional[str] = None
    created_at: datetime
    participants: list[ChatParticipantResponse]

    model_config = {"from_attributes": True}


class ChatConversationListItem(BaseModel):
    id: int
    type: str
    name: Optional[str] = None
    created_at: datetime
    participants: list[ChatParticipantResponse]
    last_message: Optional[ChatMessageResponse] = None
    unread_count: int = 0

    model_config = {"from_attributes": True}


class ChatMessagePage(BaseModel):
    messages: list[ChatMessageResponse]
    has_more: bool
    next_cursor: Optional[int] = None
