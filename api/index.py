from telethon import TelegramClient, events
from patterns import create_channel, create_group, stop, admin
from state import add_rule, Rules
from dotenv import load_dotenv
import os

#* take environment variables from .env.
load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
INVITE_LIMIT = os.getenv('INVITE_LIMIT')


add_rule(Rules.invite, int(INVITE_LIMIT), 60 * 24) # invate per day

client = TelegramClient(PHONE_NUMBER, API_ID, API_HASH)

async def message_printer(event):
    print(event.message.message)

def with_client(handler):
    return lambda event: handler(event, client)




async def main():
    await client.start()
    client.add_event_handler(message_printer, events.NewMessage())

    #* create
    client.add_event_handler(with_client(create_group), events.NewMessage(pattern="/create_group" ))
    client.add_event_handler(with_client(create_channel), events.NewMessage(pattern="/create_channel"))
    #* create

    client.add_event_handler(
        with_client(admin),
        events.NewMessage(pattern="/admin"))

    #* check
    client.add_event_handler(lambda event: event.respond("Ok"), events.NewMessage(pattern="/status"))

    #* stop
    client.add_event_handler(with_client(stop), events.NewMessage(
        pattern='/stop',
        # from_users=me.id
        ))

    print("Server is running...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())

