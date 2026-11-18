from fastapi import APIRouter, status

from app.dependencies import ConversationServiceDep, CurrentUserDep
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    ConversationUpdateRequest,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get(
    "",
    summary="Moje rozmowy, od ostatnio aktywnej",
    description="`archived=true` zwraca rozmowy z archiwum.",
)
async def list_conversations(
    conversation_service: ConversationServiceDep,
    user: CurrentUserDep,
    archived: bool = False,
) -> list[ConversationResponse]:
    conversations = await conversation_service.list_conversations(user, archived)
    return [ConversationResponse.model_validate(item) for item in conversations]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Nowa rozmowa",
    description="Bez `model` rozmowa dostaje model domyślny. Pusty tytuł uzupełni pierwszy prompt.",
)
async def create_conversation(
    request: ConversationCreateRequest,
    conversation_service: ConversationServiceDep,
    user: CurrentUserDep,
) -> ConversationResponse:
    conversation = await conversation_service.create_conversation(
        user, request.title, request.model
    )
    return ConversationResponse.model_validate(conversation)


@router.get("/{conversation_id}", summary="Szczegóły rozmowy")
async def get_conversation(
    conversation_id: str,
    conversation_service: ConversationServiceDep,
    user: CurrentUserDep,
) -> ConversationResponse:
    conversation = await conversation_service.get_conversation(user, conversation_id)
    return ConversationResponse.model_validate(conversation)


@router.patch(
    "/{conversation_id}",
    summary="Zmień tytuł, model lub archiwizuj",
    description="Wysyłasz tylko pola, które chcesz zmienić.",
)
async def update_conversation(
    conversation_id: str,
    request: ConversationUpdateRequest,
    conversation_service: ConversationServiceDep,
    user: CurrentUserDep,
) -> ConversationResponse:
    conversation = await conversation_service.update_conversation(user, conversation_id, request)
    return ConversationResponse.model_validate(conversation)


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń rozmowę razem z wiadomościami",
)
async def delete_conversation(
    conversation_id: str,
    conversation_service: ConversationServiceDep,
    user: CurrentUserDep,
) -> None:
    await conversation_service.delete_conversation(user, conversation_id)
