from telethon import TelegramClient, Button, events
from telethon.tl.functions.channels import InviteToChannelRequest , JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from telethon.tl.types import InputPeerUser

api_id = '25972343'
api_hash = 'b63ab3e95f8967da1fb862688c2316c5'

# Use your phone number instead of a bot token
client = TelegramClient('+380978012740', api_id, api_hash)

async def main():
    await client.start()
    me = await client.get_me()

    @client.on(events.NewMessage(pattern="@"))

    async def handle_usernames(event):
        usernames = event.raw_text.split()
        # Get the entity of your group (replace 'your_group' with your group's username)
        group = await client.get_entity('https://t.me/+wuBc4gVbLl02MzMy')

        # # Create a list to hold the user entities
        users = []

        # # For each username, get the user entity and add it to the list
        for username in usernames:
            user = await client.get_entity(username)
            users.append(InputPeerUser(user.id, user.access_hash))
            await event.respond(f"You entered these usernames: {usernames}")
            print(usernames)

        # # Use InviteToChannelRequest to add the users to the group
        await client(InviteToChannelRequest(group, users))



    print("run server")
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
