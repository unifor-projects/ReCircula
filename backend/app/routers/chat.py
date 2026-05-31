from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models.chat import ChatConversation, ChatConversationType, ChatMessage, ChatParticipant
from app.models.usuario import Usuario
from app.schemas.chat import (
    ChatConversationCreate,
    ChatConversationListItem,
    ChatConversationResponse,
    ChatMessagePage,
    ChatMessageResponse,
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


def _assert_participant(conversation_id: int, user_id: int, db: Session) -> ChatParticipant:
    participant = (
        db.query(ChatParticipant)
        .filter(
            ChatParticipant.conversation_id == conversation_id,
            ChatParticipant.user_id == user_id,
        )
        .first()
    )
    if not participant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")
    return participant


@router.post(
    "/conversations",
    response_model=ChatConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar conversa direta",
)
def create_conversation(
    data: ChatConversationCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if data.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível iniciar conversa consigo mesmo",
        )

    other_user = db.get(Usuario, data.user_id)
    if not other_user or not other_user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    existing = (
        db.query(ChatConversation)
        .join(ChatParticipant, ChatParticipant.conversation_id == ChatConversation.id)
        .filter(
            ChatConversation.type == ChatConversationType.direct,
            ChatParticipant.user_id == current_user.id,
        )
        .intersect(
            db.query(ChatConversation)
            .join(ChatParticipant, ChatParticipant.conversation_id == ChatConversation.id)
            .filter(
                ChatConversation.type == ChatConversationType.direct,
                ChatParticipant.user_id == data.user_id,
            )
        )
        .first()
    )
    if existing:
        conv = (
            db.query(ChatConversation)
            .options(selectinload(ChatConversation.participants).selectinload(ChatParticipant.user))
            .filter(ChatConversation.id == existing.id)
            .first()
        )
        return conv

    conversation = ChatConversation(type=ChatConversationType.direct)
    db.add(conversation)
    db.flush()

    db.add(ChatParticipant(conversation_id=conversation.id, user_id=current_user.id))
    db.add(ChatParticipant(conversation_id=conversation.id, user_id=data.user_id))
    db.commit()

    return (
        db.query(ChatConversation)
        .options(selectinload(ChatConversation.participants).selectinload(ChatParticipant.user))
        .filter(ChatConversation.id == conversation.id)
        .first()
    )


@router.get(
    "/conversations",
    response_model=list[ChatConversationListItem],
    summary="Listar conversas do usuário",
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    my_conv_ids = (
        db.query(ChatParticipant.conversation_id)
        .filter(ChatParticipant.user_id == current_user.id)
        .subquery()
    )

    conversations = (
        db.query(ChatConversation)
        .options(selectinload(ChatConversation.participants).selectinload(ChatParticipant.user))
        .filter(ChatConversation.id.in_(my_conv_ids))
        .all()
    )

    last_msg_sub = (
        db.query(
            ChatMessage.conversation_id,
            func.max(ChatMessage.id).label("max_id"),
        )
        .group_by(ChatMessage.conversation_id)
        .subquery()
    )
    last_messages_rows = (
        db.query(ChatMessage)
        .join(last_msg_sub, ChatMessage.id == last_msg_sub.c.max_id)
        .options(selectinload(ChatMessage.sender))
        .all()
    )
    last_messages = {m.conversation_id: m for m in last_messages_rows}

    my_participants = (
        db.query(ChatParticipant)
        .filter(
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.conversation_id.in_(my_conv_ids),
        )
        .all()
    )
    last_read_map = {p.conversation_id: p.last_read_at for p in my_participants}

    result = []
    for conv in conversations:
        last_msg = last_messages.get(conv.id)
        last_read = last_read_map.get(conv.id)

        unread_q = db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.conversation_id == conv.id,
            ChatMessage.sender_id != current_user.id,
        )
        if last_read:
            unread_q = unread_q.filter(ChatMessage.created_at > last_read)
        unread_count = unread_q.scalar() or 0

        item = ChatConversationListItem.model_validate(conv)
        item.last_message = ChatMessageResponse.model_validate(last_msg) if last_msg else None
        item.unread_count = unread_count
        result.append(item)

    result.sort(
        key=lambda c: c.last_message.created_at if c.last_message else c.created_at,
        reverse=True,
    )
    return result


@router.get(
    "/conversations/{conversation_id}",
    response_model=ChatConversationResponse,
    summary="Detalhes de uma conversa",
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    _assert_participant(conversation_id, current_user.id, db)
    conv = (
        db.query(ChatConversation)
        .options(selectinload(ChatConversation.participants).selectinload(ChatParticipant.user))
        .filter(ChatConversation.id == conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")
    return conv


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=ChatMessagePage,
    summary="Histórico de mensagens (cursor pagination)",
)
def get_messages(
    conversation_id: int,
    cursor: int | None = Query(None, description="ID da última mensagem carregada"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    _assert_participant(conversation_id, current_user.id, db)

    query = (
        db.query(ChatMessage)
        .options(selectinload(ChatMessage.sender))
        .filter(ChatMessage.conversation_id == conversation_id)
    )

    if cursor:
        query = query.filter(ChatMessage.id < cursor)

    messages = query.order_by(ChatMessage.id.desc()).limit(limit + 1).all()

    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]

    messages.reverse()

    return ChatMessagePage(
        messages=[ChatMessageResponse.model_validate(m) for m in messages],
        has_more=has_more,
        next_cursor=messages[0].id if messages and has_more else None,
    )


@router.get(
    "/users/search",
    summary="Buscar usuários para iniciar conversa",
)
def search_users(
    q: str = Query(..., min_length=1, max_length=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    users = (
        db.query(Usuario)
        .filter(
            Usuario.id != current_user.id,
            Usuario.is_active.is_(True),
            or_(
                Usuario.nome.ilike(f"%{q}%"),
                Usuario.email.ilike(f"%{q}%"),
            ),
        )
        .limit(20)
        .all()
    )
    return [
        {
            "id": u.id,
            "nome": u.nome,
            "foto_url": u.foto_url,
            "localizacao": u.localizacao,
        }
        for u in users
    ]


@router.get("/unread-count", summary="Total de mensagens não lidas")
def unread_count(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    my_participations = (
        db.query(ChatParticipant)
        .filter(ChatParticipant.user_id == current_user.id)
        .all()
    )

    total = 0
    for p in my_participations:
        q = db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.conversation_id == p.conversation_id,
            ChatMessage.sender_id != current_user.id,
        )
        if p.last_read_at:
            q = q.filter(ChatMessage.created_at > p.last_read_at)
        total += q.scalar() or 0

    return {"total_unread": total}
