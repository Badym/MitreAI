from beanie import PydanticObjectId

from app.models.message import Message


class MessageRepository:
    async def list_by_conversation(self, conversation_id: PydanticObjectId) -> list[Message]:
        return (
            await Message.find(Message.conversation_id == conversation_id)
            .sort("+created_at", "+_id")
            .to_list()
        )

    async def create(self, message: Message) -> Message:
        return await message.insert()

    async def delete_by_conversation(self, conversation_id: PydanticObjectId) -> None:
        await Message.find(Message.conversation_id == conversation_id).delete()
