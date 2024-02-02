from telethon import TelegramClient, events
from patterns import create_channel, create_group,  handle_usernames
import spam
from shared import stop, rules

global client

__api_id = '20921653'
__api_hash = '4f70d910d762a37ae6703e370f861a7a'
__phone_number = '+380501061373'


spam.add_rule(rules["message"], 30, 1) # to different users per minute
spam.add_rule(rules["invate"], 100, 60 * 24) # invate per day

client = TelegramClient(__phone_number, __api_id, __api_hash)

async def __message_checker(event):
    print(event.message.message)



async def main():
    await client.start()
    client.add_event_handler(__message_checker, events.NewMessage())
    client.add_event_handler(lambda event: stop(event, client), events.NewMessage(pattern='/stop'))

    # client.add_event_handler(handle_usernames, events.NewMessage(pattern="/add"))
    # client.add_event_handler(create_group, events.NewMessage(pattern="/create_group"))
    client.add_event_handler(lambda event: create_channel(event, client), events.NewMessage(pattern="/create_channel"))

    print("Server is running...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
