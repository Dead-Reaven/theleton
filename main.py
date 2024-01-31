from telethon import TelegramClient, events
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.types import InputPeerChannel

api_id = '25972343'
api_hash = 'b63ab3e95f8967da1fb862688c2316c5'
phone_number = '+380978012740'

client = TelegramClient(phone_number, api_id, api_hash)

async def handle_usernames(event):
    usernames = event.raw_text.split()
    group = await client.get_entity('https://t.me/+wuBc4gVbLl02MzMy')
    target_group_entity = InputPeerChannel(channel_id=group.id, access_hash=group.access_hash)

    for username in usernames:
        try:
            user = await client.get_entity(username)
            await client(InviteToChannelRequest(target_group_entity, [user]))
            await event.respond(f"You entered these usernames: {usernames}")
        except ValueError:
            await event.respond(f"Cannot find: {username}")

async def create_group(event):
    args = event.message.message.split()[1:]
    group_name = args[0]
    users = args[1:]

    user_entities = [await client.get_entity(username) for username in users]
    newChat = await client(CreateChatRequest(users=user_entities, title=group_name))

    await event.respond(f"Group '{group_name}' created with ID {newChat.chats[0].id}")

async def main():
    await client.start()
    client.add_event_handler(handle_usernames, events.NewMessage(pattern="@"))
    client.add_event_handler(create_group, events.NewMessage(pattern="/create_group"))
    print("Server is running...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
