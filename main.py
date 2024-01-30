from telethon import TelegramClient, Button, events
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact, InputPeerUser, InputPeerEmpty, InputPeerChannel
from telethon.tl.functions.messages import GetDialogsRequest


api_id = '25972343'
api_hash = 'b63ab3e95f8967da1fb862688c2316c5'

# Use your phone number instead of a bot token
client = TelegramClient('+380978012740', api_id, api_hash)




async def main():
    await client.start()
    me = await client.get_me()

    #! from invate
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    # result = await client(GetDialogsRequest(
    #     offset_date=last_date,
    #     offset_id=0,
    #     offset_peer=InputPeerEmpty(),
    #     limit=chunk_size,
    #     hash=0
    # ))

    # chats.extend(result.chats)
    # print(result.chats)
    #! from invate

    @client.on(events.NewMessage(pattern="@"))
    async def handle_usernames(event):
        usernames = event.raw_text.split()
        # Get the entity of your group (replace 'your_group' with your group's username)
        # InputPeerChannel()
        group = await client.get_entity('https://t.me/+wuBc4gVbLl02MzMy')
        target_group_entity = InputPeerChannel(channel_id=group.id, access_hash=group.access_hash)
        # Create a list to hold the user entities
        users = []
        # For each username, get the user entity and add it to the list
        for username in usernames:
            try:
                user = await client.get_entity(username)
            except ValueError:
                return await event.respond(f"cannot find: {username}")

            # users.append(InputPeerUser(user.id, user.access_hash))
            await event.respond(f"You entered these usernames: {usernames}")

            await client(InviteToChannelRequest(target_group_entity, [user]))
            print(usernames)

        # Use InviteToChannelRequest to add the users to the group

        #* user_to_add = client.get_input_entity(user['username'])
        #* user_to_add = InputPeerUser(user['id'], user['access_hash'])
        # await client(InviteToChannelRequest(group, users))

    print("run server")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
