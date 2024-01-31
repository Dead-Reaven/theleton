from telethon import TelegramClient, Button, events
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact, InputPeerUser, InputPeerEmpty, InputPeerChannel
from telethon.tl.functions.messages import GetDialogsRequest, CreateChatRequest


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
        # InputPeerChannel()
        group = await client.get_entity('https://t.me/+wuBc4gVbLl02MzMy')
        target_group_entity = InputPeerChannel(channel_id=group.id, access_hash=group.access_hash)

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
        #? methods to get user
        #* user_to_add = client.get_input_entity(user['username'])
        #* user_to_add = InputPeerUser(user['id'], user['access_hash'])
        #? methods to get user
        #! exeption error handling
        # await client(InviteToChannelRequest(group, users))
	    # except PeerFloodError:
	    #     print(re+"[!] Getting Flood Error from telegram. \n[!] Script is stopping now. \n[!] Please try again after some time.")
	    # except UserPrivacyRestrictedError:
	    #     print(re+"[!] The user's privacy settings do not allow you to do this. Skipping.")
	    # except:
	    #     traceback.print_exc()
	    #     print(re+"[!] Unexpected Error")
	    #     continue
        #! exeption error handling




    @client.on(events.NewMessage(pattern="/create_group"))
    async def create_group(event):
        # Get the command arguments (group name and users)
        args = event.message.message.split()[1:]
        group_name = args[0]
        users = args[1:]

        # Get the user entities
        user_entities = []
        for username in users:
            print(username)
            user = await client.get_entity(username)
            user_entities.append(user)

        # Create the group
        result = await client(CreateChatRequest(users=user_entities, title=group_name))

        # Respond with the created group's ID
        await event.respond(f"Group '{group_name}' created with ID {result.chats[0].id}")



    print("run server")
    await client.run_until_disconnected()
with client:
    client.loop.run_until_complete(main())
