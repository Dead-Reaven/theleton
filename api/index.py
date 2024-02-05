from telethon import TelegramClient, events
from patterns import test_handle_usernames, create_channel, create_group, stop
from state import add_rule, Rules

__api_id = '20921653'
__api_hash = '4f70d910d762a37ae6703e370f861a7a'
__phone_number = '+380501061373'

add_rule(Rules.message, 30, 1) # to different users per minute
add_rule(Rules.get_entity, 5, 1)
add_rule(Rules.invite, 100, 60 * 24) # invate per day

client = TelegramClient(__phone_number, __api_id, __api_hash)

async def message_printer(event):
    print(event.message.message)

def with_client(handler):
    return lambda event: handler(event, client)


async def main():
    await client.start()
    me = await client.get_me()

    client.add_event_handler(message_printer, events.NewMessage())

    #* create
    client.add_event_handler(with_client(create_group), events.NewMessage(pattern="/create_group" ))
    client.add_event_handler(with_client(create_channel), events.NewMessage(pattern="/create_channel"))
    #* create

    #* add users
    client.add_event_handler(
        with_client(test_handle_usernames),
        events.NewMessage(pattern="/add", from_users=me.id))

    #* check
    client.add_event_handler(lambda event: event.respond("Ok"), events.NewMessage(pattern="/status"))

    #* stop
    client.add_event_handler(with_client(stop), events.NewMessage(pattern='/stop', from_users=me.id))

    print("Server is running...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())

