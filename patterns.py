from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.functions.channels import InviteToChannelRequest, CreateChannelRequest
from telethon.tl.functions.messages import CreateChatRequest, AddChatUserRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.types import InputPeerChannel, InputPeerChat, Channel, Chat

from time import sleep
import random
#* custom modules

from spam import Rules, call, ErrorLimitCall

#per each iteration
min_time_wait = 2
max_time_wait = 5
sleep_time = 3

async def handle_usernames(event: NewMessage.Event, client: TelegramClient):
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
                await call(Rules.invate)
                await client(InviteToChannelRequest(target_group_entity, [user]))
            elif isinstance(group, Chat):
                await call(Rules.invate)
                await client(AddChatUserRequest(chat_id=group.id, user_id=user, fwd_limit=10))
            #? invate call

            await event.respond(f"{username} has been added. Waiting for 10-30 seconds...")
            sleep(random.randrange(10, 30))

        except ValueError as e:
            await event.respond(f"Cannot find: {username} --- {e}")

        #! errors with privacy
        except PeerFloodError:
            await event.respond(f"{username} Getting flood error from telegram. Invating is stoping now. Please, try run later. Reccomend await 1-3 hour or better one day to prevent ban")
            await stop(event)
            print("peer flood error")


        except UserPrivacyRestrictedError:
            await event.respond("The user's privacy settings do not allow you to do this. Skipping.")
            print("error user privacy restricted. Skip")

        except Exception as e:
            await event.respond(f"Unexpected error at user: [{username}]. --- {e} --- server disconected")
            await stop(event)
            print(e)


    await event.respond(f"You entered these usernames: {users}")

async def create_group(event: NewMessage.Event, client: TelegramClient):
    args = event.message.message.split()[1:]
    group_name = args[0]
    users = args[1:]

    user_entities = [await client.get_entity(username) for username in users]
    newChat = await client(CreateChatRequest(users=user_entities, title=group_name))

    await event.respond(f"Group '{group_name}' created with ID {newChat.chats[0].id}")

async def create_channel(event: NewMessage.Event, client: TelegramClient):
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




async def test_handle_usernames(event: NewMessage.Event, client: TelegramClient):
    args = event.message.message.split()[1:]

    group_name = args[0]

    users = args[1:]

    added_users = []
    lost_users = args[1:]
    l = len(users)
    #calc minuts
    min_t = (min_time_wait * l + sleep_time * l) / 60
    max_t = (max_time_wait*l + sleep_time * l) / 60

    msg = f"""Request to add {users}
    please wait: {round(min_t, 1)} - {round(max_t, 1)} mins"""

    await event.respond(msg)
    for username in users:
        sleep(sleep_time)
        try:
            #! write you solution here!
            # await call(
            #     Rules.get_entity,
            #     lambda : print(f"{username} has been added. Waiting for 2-5 seconds...")
            # )

            added_users.append(username)
            lost_users.remove(username)
            sleep(random.randrange(min_time_wait, max_time_wait))

        #* skip on value error
        except ValueError as e:
            await event.respond(f"Cannot find: {username} --- {e};")

        #* skip on privacy error
        except UserPrivacyRestrictedError:
            await event.respond(f"[{username}] This user privacy settings do not allow you to do this. Skipping.")
            print("error user privacy restricted. Skip")

        #? break on limit error
        except ErrorLimitCall as e:
            await event.respond(f"[{username}]: {e}")
            await event.respond(f"not added users: {lost_users}")
            break

        #! stop server on critical Flood Error
        except PeerFloodError as e:
            await event.respond(f"{username} Getting flood error from telegram. Invating is stoping now. Please, try run later. Reccomend await 1-3 hour or better one day to prevent ban")
            await event.respond(f"not added users: {lost_users}")
            await stop(event)
            print("peer flood error:", str(e))

        #! stop server on unexpected error
        except Exception as e:
            await event.respond(f"Unexpected error at user: [{username}]. --- {e} --- server disconected")
            await event.respond(f"not added users: {lost_users}")
            await stop(event, client)
            print(e)

    #*finally massage responce
    msg = f"""
    Succesefuly invited these usernames: {added_users}
    lost: {lost_users if lost_users.__len__() > 0 else "No lost users" }
    added:{added_users.__len__()}; lost:{lost_users.__len__()} """
    await event.respond(msg)


async def stop(event, client):
    await client.disconnect()

