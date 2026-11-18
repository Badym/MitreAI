from beanie import PydanticObjectId
from bson import ObjectId

from app.models.conversation import Conversation


class ConversationRepository:
    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        if not ObjectId.is_valid(conversation_id):
            return None
        return await Conversation.get(PydanticObjectId(conversation_id))

    async def list_by_user(self, user_id: PydanticObjectId, archived: bool) -> list[Conversation]:
        return (
            await Conversation.find(
                Conversation.user_id == user_id,
                Conversation.is_archived == archived,
            )
            .sort("-updated_at")
            .to_list()
        )

    async def create(self, conversation: Conversation) -> Conversation:
        return await conversation.insert()

    async def save(self, conversation: Conversation) -> Conversation:
        return await conversation.save()

    async def delete(self, conversation: Conversation) -> None:
        await conversation.delete()
