from telethon import TelegramClient, events
from telethon.tl.functions.channels import InviteToChannelRequest, CreateChannelRequest
from telethon.tl.functions.messages import CreateChatRequest, AddChatUserRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.types import InputPeerChannel, InputPeerChat, Channel, Chat
from time import sleep
import random
import spam

api_id = ''
api_hash = ''
phone_number = ''

rules = {
    "message" : 'send_message',
    "invate" : 'send_invate',
}

spam.add_rule(rules["message"], 30, 1) # to different users per minute
spam.add_rule(rules["invate"], 100, 60 * 24) # invate per day



client = TelegramClient(phone_number, api_id, api_hash)


async def handle_usernames(event):
    args = event.message.message.split()[1:]
    group_name = args[0]
    users = args[1:]

    group = await client.get_entity(group_name)
    print("group:", group)
    if isinstance(group, Channel):
        target_group_entity = InputPeerChannel(channel_id=group.id, access_hash=group.access_hash)
    elif isinstance(group, Chat):
        target_group_entity = InputPeerChat(chat_id=group.id)
    else:
        return await event.respond(f"Unknown group type: {type(group).__name__}")

    for username in users:
        sleep(3)
        try:
            user = await client.get_entity(username)
            #? invate call
            if isinstance(group, Channel):
                await spam.call(rules["invate"])
                await client(InviteToChannelRequest(target_group_entity, [user]))
            elif isinstance(group, Chat):
                spam.call(rules["invate"])
                await client(AddChatUserRequest(chat_id=group.id, user_id=user, fwd_limit=10))
            #? invate call

            await event.respond(f"{username} has been added. Waiting for 10-30 seconds...")
            sleep(random.randrange(10, 30))

        except ValueError as e:
            await event.respond(f"Cannot find: {username} --- {e}")
        #! errors with privacy
        except PeerFloodError:
            await event.respond(f"{username} Getting flood error from telegram. Invating is soping now. Please, try run later. Reccomend await 1-3 hour or better one day to prevent ban")
            await client.disconnect()
            print("peer flood error")
            exit(1)

        except UserPrivacyRestrictedError:
            await event.respond("The user's privacy settings do not allow you to do this. Skipping.")
            print("error user privacy restricted. Skip")

        except Exception as e:
            await event.respond(f"Unexpected error at user: [{username}]. --- {e} --- server disconected")
            await client.disconnect()
            print(e)
            exit(1)

    await event.respond(f"You entered these usernames: {users}")

async def create_group(event):
    args = event.message.message.split()[1:]
    group_name = args[0]
    users = args[1:]

    user_entities = [await client.get_entity(username) for username in users]
    newChat = await client(CreateChatRequest(users=user_entities, title=group_name))

    await event.respond(f"Group '{group_name}' created with ID {newChat.chats[0].id}")



async def create_channel(event):
    args = event.message.message.split()[1:]
    channel_name = args[0]
    about = ' '.join(args[1:])  # The rest of the arguments will be the channel's about text

    # Create the channel
    result = await client(CreateChannelRequest(
        title=channel_name,
        about=about,
        megagroup=True  # Set this to True to create a supergroup
    ))

    # Respond with the created channel's ID
    await event.respond(f"Channel '{channel_name}' created with ID {result.chats[0].id}")


async def message_checker(event):
    print(event.message.message)

async def main():
    await client.start()
    client.add_event_handler(message_checker, events.NewMessage())
    client.add_event_handler(handle_usernames, events.NewMessage(pattern="/add"))
    client.add_event_handler(create_group, events.NewMessage(pattern="/create_group"))
    client.add_event_handler(create_channel, events.NewMessage(pattern="/create_channel"))

    print("Server is running...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
