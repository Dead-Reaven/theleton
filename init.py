from telethon import TelegramClient, events
from patterns import test_handle_usernames, create_channel, create_group,  handle_usernames, stop
import spam

__api_id = '20921653'
__api_hash = '4f70d910d762a37ae6703e370f861a7a'
__phone_number = '+380501061373'

spam.add_rule(spam.Rules.message, 30, 1) # to different users per minute
spam.add_rule(spam.Rules.get_entity, 20, 1)
spam.add_rule(spam.Rules.invate, 100, 60 * 24) # invate per day

client = TelegramClient(__phone_number, __api_id, __api_hash)

async def __message_checker(event):
    print(event.message.message)

def with_client(handler):
    return lambda event: handler(event, client)

async def main():
    await client.start()
    client.add_event_handler(__message_checker, events.NewMessage())

    #* create
    client.add_event_handler(with_client(create_group), events.NewMessage(pattern="/create_group"))
    client.add_event_handler(with_client(create_channel), events.NewMessage(pattern="/create_channel"))
    #* create

    #* oparate
    client.add_event_handler(with_client(stop), events.NewMessage(pattern='/stop'))
    client.add_event_handler(with_client(test_handle_usernames), events.NewMessage(pattern="/add"))
    # client.add_event_handler(with_client(handle_usernames), events.NewMessage(pattern="/add"))
    #* oparate
    print("Server is running...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())

