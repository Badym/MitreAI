from dataclasses import dataclass

from app.llm.provider import LLMProvider
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.models.user import User
from app.repositories.message_repository import MessageRepository
from app.services.conversation_service import ConversationService
from app.services.model_service import ModelService


@dataclass(frozen=True)
class SentMessage:
    user_message: Message
    assistant_message: Message
    conversation: Conversation


class MessageService:
    def __init__(
        self,
        conversations: ConversationService,
        messages: MessageRepository,
        models: ModelService,
        provider: LLMProvider,
    ) -> None:
        self._conversations = conversations
        self._messages = messages
        self._models = models
        self._provider = provider

    async def list_messages(self, user: User, conversation_id: str) -> list[Message]:
        conversation = await self._conversations.get_conversation(user, conversation_id)
        return await self._messages.list_by_conversation(conversation.id)

    async def send_message(
        self, user: User, conversation_id: str, content: str, model: str | None
    ) -> SentMessage:
        conversation = await self._conversations.get_conversation(user, conversation_id)
        model = self._models.resolve(model or conversation.model)

        user_message = await self._messages.create(
            Message(conversation_id=conversation.id, role=MessageRole.USER, content=content)
        )
        history = await self._messages.list_by_conversation(conversation.id)
        reply = await self._provider.generate(model, history)
        assistant_message = await self._messages.create(
            Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=reply.content,
                model=model,
                tokens_in=reply.tokens_in,
                tokens_out=reply.tokens_out,
                analysis=reply.analysis,
            )
        )

        conversation = await self._conversations.register_message(conversation, model, content)
        return SentMessage(user_message, assistant_message, conversation)
