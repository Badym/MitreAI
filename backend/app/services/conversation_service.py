from app.core.exceptions import NotFoundError
from app.models.common import utc_now
from app.models.conversation import Conversation
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.conversation import ConversationUpdateRequest
from app.services.model_service import ModelService

TITLE_MAX_LENGTH = 60


def title_from_prompt(prompt: str) -> str:
    first_line = prompt.strip().splitlines()[0]
    if len(first_line) <= TITLE_MAX_LENGTH:
        return first_line
    return first_line[: TITLE_MAX_LENGTH - 1].rstrip() + "…"


class ConversationService:
    def __init__(
        self,
        conversations: ConversationRepository,
        messages: MessageRepository,
        models: ModelService,
    ) -> None:
        self._conversations = conversations
        self._messages = messages
        self._models = models

    async def list_conversations(self, user: User, archived: bool = False) -> list[Conversation]:
        return await self._conversations.list_by_user(user.id, archived)

    async def create_conversation(self, user: User, title: str, model: str | None) -> Conversation:
        conversation = Conversation(user_id=user.id, title=title, model=self._models.resolve(model))
        return await self._conversations.create(conversation)

    async def get_conversation(self, user: User, conversation_id: str) -> Conversation:
        conversation = await self._conversations.get_by_id(conversation_id)
        if conversation is None or conversation.user_id != user.id:
            raise NotFoundError("Nie znaleziono rozmowy")
        return conversation

    async def update_conversation(
        self, user: User, conversation_id: str, changes: ConversationUpdateRequest
    ) -> Conversation:
        conversation = await self.get_conversation(user, conversation_id)

        if changes.title is not None:
            conversation.title = changes.title
        if changes.model is not None:
            conversation.model = self._models.resolve(changes.model)
        if changes.is_archived is not None:
            conversation.is_archived = changes.is_archived

        return await self._conversations.save(conversation)

    async def delete_conversation(self, user: User, conversation_id: str) -> None:
        conversation = await self.get_conversation(user, conversation_id)
        await self._messages.delete_by_conversation(conversation.id)
        await self._conversations.delete(conversation)

    async def register_message(
        self, conversation: Conversation, model: str, prompt: str
    ) -> Conversation:
        conversation.model = model
        conversation.updated_at = utc_now()
        if not conversation.title:
            conversation.title = title_from_prompt(prompt)
        return await self._conversations.save(conversation)
