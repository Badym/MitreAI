from typing import Annotated

from fastapi import APIRouter, Form, status

from app.dependencies import CurrentUserDep, MessageServiceDep
from app.schemas.conversation import ConversationResponse
from app.schemas.message import MessageCreateForm, MessageResponse, SendMessageResponse

router = APIRouter(prefix="/conversations/{conversation_id}/messages", tags=["messages"])


@router.get("", summary="Wiadomości rozmowy, od najstarszej")
async def list_messages(
    conversation_id: str,
    message_service: MessageServiceDep,
    user: CurrentUserDep,
) -> list[MessageResponse]:
    messages = await message_service.list_messages(user, conversation_id)
    return [MessageResponse.model_validate(message) for message in messages]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Wyślij prompt i odbierz odpowiedź modelu",
    description="Bez `model` odpowiada model rozmowy. Na razie odpowiada atrapa modelu.",
)
async def send_message(
    conversation_id: str,
    form: Annotated[MessageCreateForm, Form()],
    message_service: MessageServiceDep,
    user: CurrentUserDep,
) -> SendMessageResponse:
    sent = await message_service.send_message(user, conversation_id, form.content, form.model)
    return SendMessageResponse(
        user_message=MessageResponse.model_validate(sent.user_message),
        assistant_message=MessageResponse.model_validate(sent.assistant_message),
        conversation=ConversationResponse.model_validate(sent.conversation),
    )
