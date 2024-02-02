rules = {
    "message" : 'send_message',
    "invate" : 'send_invate',
}

async def stop(event, client):
    await client.disconnect()

