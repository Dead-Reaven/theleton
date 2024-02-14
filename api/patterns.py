from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.functions.channels import EditAdminRequest, InviteToChannelRequest, CreateChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import CreateChatRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.types import ChatAdminRights, ChannelParticipantsSearch

from time import sleep
import random
#* custom modules
#! тимчасово не використовується так як не вдається стабільно додавати (можна ігнорувати цей модуль)
from state import Rules, call, ErrorLimitCall
from dotenv import load_dotenv
import os

#* take environment variables from .env.
load_dotenv()
#per each iteration
MIN_TIME_WAIT = int(os.getenv('MIN_TIME_WAIT'))
MAX_TIME_WAIT = int(os.getenv('MAX_TIME_WAIT'))
SLEEP_TIME = int(os.getenv('SLEEP_TIME'))

# Assuming 'user_to_add' is the user you added and want to promote
# and 'channel' is the entity of the channel where you want to add the admin

#* super invite
# await client(EditAdminRequest(channel, user_to_add, rights, 'to_remove'))
# sleep(5)
# print(f"{username} add as admin req send")
#* remove req
# await client(EditAdminRequest(channel, user_to_add, remove_right, 'to_remove'))
# print(f"{username} remove admin req send")
# rights = ChatAdminRights(invite_users=True)
# remove_right = ChatAdminRights(invite_users=False)

async def admin(event: NewMessage.Event, client: TelegramClient):
    global MIN_TIME_WAIT, MAX_TIME_WAIT, SLEEP_TIME
    args = event.message.message.split()[1:]
    group_name = args[0]
    users = args[1:]

    counter = 0
    flood_counter = 0
    # Get the channel
    try:
        channel = await client.get_entity(group_name)
    except Exception as e:
        return await event.respond(str(e))

    await event.respond(f"🔍 start ...\n inviting {len(users)} users ... ")


    l = len(users)
    #calc minuts
    min_t = (MIN_TIME_WAIT * l + SLEEP_TIME * l) / 60
    max_t = (MAX_TIME_WAIT*l + SLEEP_TIME * l) / 60

    msg = f"""Request to add {users}
    please wait: {round(min_t, 1)} - {round(max_t, 1)} mins"""

    await event.respond(msg)

    users_entity = []
    i = 0
    for username in users:
        i += 1
        sleep(random.randrange(MIN_TIME_WAIT, MAX_TIME_WAIT) if i > 1 else 0)
        # sleep(3)
        try:
            user_to_add = await client.get_entity(username)
            users_entity.append(user_to_add)
            print(f"add [{username}] join list")
            # sleep(3)
            #*sample invite
            # print(f"[{username}] invite send. next... please wait")
            # counter += 1

        #* skip on value error
        except ValueError as e:
            # await event.respond(f"Cannot find: {username} --- {e};")
            print(f"Cannot find: {username} --- {e};")

        #* skip on privacy error
        except UserPrivacyRestrictedError as e:
            # await event.respond(f"[{username}] {str(e)}")
            print(f"[{username}] {str(e)}: error user privacy restricted.  Skip")

        #? break on limit error
        except ErrorLimitCall as e:
            await event.respond(f"[{username}]: {e}")
            print(f"[{username}]: {e}")
            break

        #! stop server on critical Flood Error
        except PeerFloodError as e:
            await event.respond(f"{username} - err: {str(e)}; Getting flood error from telegram. Invating is stoping now. Please, try run later. Reccomend await 1-3 hour or better one day to prevent ban")
            flood_counter += 1
            if flood_counter > 2:
                await stop(event, client)
            else:
                MIN_TIME_WAIT += 5
                MAX_TIME_WAIT += 10


            print(f"peer flood error [{flood_counter}]:", str(e))

        #! stop server on unexpected error
        except Exception as e:
            if ("A wait of" in str(e)):
                await event.respond(f"{str(e)}")
                await stop(event, client)
                break
            else:
                await event.respond(f"Unexpected error at user: [{username}]")
                # await stop(event, client)
                await event.respond(f"{str(e)}")
            print(e)

    print("--- Sleep before invite to channel request--- \n")
    sleep(10)
    try:
        result = await client(InviteToChannelRequest(channel, users_entity))
        participants_usernames = [participant.__dict__ for participant in result.users]
        print(participants_usernames)

    except Exception as e:
        await event.respond(f"Error on invite list: {e}")
        print(e)

    await check(event, client, channel, users)

    # *finally massage responce
    # responce = await check_users(event, client)

    await event.respond(f"Added {counter} users. Please check it in scaner bot")


async def stop(event, client):
    await event.respond(f"--- server disconected ---")
    await client.disconnect()


async def check(event, client, channel, users_to_check):

    channel = await client.get_entity(channel)
    participants = await client(GetParticipantsRequest(
        channel, ChannelParticipantsSearch(''), offset=0, limit=500, hash=0
    ))
    participants_usernames = [participant.username for participant in participants.users]
    print(participants.users)

    add = []
    lost = []
    for user in users_to_check:
        if user in participants_usernames:
            print(f"{user} is a participant in the channel")
            add.append(user)
        else:
            print(f"{user} is not a participant in the channel")
            lost.append(user)

    print(f"add {len(add)} users")
    print(f"lost {len(lost)} users")
    await event.respond(f"add {len(add)} users\nlost {len(lost)} users")

# methods to check users automaticly
# removed to another bot:https://t.me/Test_Remover_Bot

# class CheckInfo:
#         def __init__(self, add, lost ):
#             self.add = add
#             self.lost = lost

#             self.msg = f"""✔️ find: {' '.join(add)}
#             ❌ lost: {' '.join(lost) if lost.__len__() > 0 else "No lost users" }
#             📋 added:{add.__len__()}; lost:{lost.__len__()} """


# async def check_users(event, client):
#     # Check if the user has been added
#     args = event.message.message.split()[1:]

#     channel = args[0]
#     users = args[1:]

#     add = []
#     lost = users[:]

#     print(f"🔍 search start {len(users)} users", )
#     await event.respond(f"🔍 search start {len(users)} users")

#     for name in users:
#         sleep(1)
#         print(f"searched:{name}")
#         async for user in client.iter_participants(channel, search=name):
#             print(name, user.username)
#             if (user.username.removeprefix("@") == name.removeprefix("@")):
#                 print(f"✔️ find: {user.username}")
#                 add.append(name)
#                 lost.remove(name)

#     Info = CheckInfo(add, lost)
#     print(Info.msg, "\n🔍 search end" )
#     await event.respond(Info.msg)
#     return Info


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

