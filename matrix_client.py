#from nio import AsyncClient

#class CustomMatrixClient(AsyncClient):
#    def __init__(self, homeserver, user_id, access_token):
#        super().__init__(homeserver)

#        self.access_token = access_token
#        self.user_id = user_id

from nio import AsyncClient, RoomMessageText

async def setup_matrix_client(config):
    client = AsyncClient(config["homeserver"], config["user_id"])
    client.access_token = config["access_token"]
    client.user_id = config["user_id"]
    client.device_id = "AAAAAAAAAA"

    client.add_event_callback(on_message, RoomMessageText)

    return client


async def on_message(room, event):
    if not event.body.startswith("!"):
        return

    message_body = event.body[1:]
    command = message_body.split(" ")[0]

    if command == "set_keywords":
        checker_type, new_keywords = message_body.split(" ")[1], " ".join(message_body.split(" ")[2:])
        await handle_set_keywords(event, checker_type, new_keywords)
        
async def handle_set_keywords(event, checker_type, new_keywords):
    sender = event["sender"]
    user_config = find_user_config_by_sender(sender)

    if not user_config:
        await client.room_send(user_config["matrix_room_id"], "m.room.message", {"msgtype": "m.text", "body": "You are not a registered user."})
        return

    checker_config = find_checker_config(user_config, checker_type)

    if not checker_config:
        await client.room_send(user_config["matrix_room_id"], "m.room.message", {"msgtype": "m.text", "body": f"No checker of type '{checker_type}' found."})
        return

    checker_config["keywords"] = new_keywords.split(",")

    await client.room_send(user_config["matrix_room_id"], "m.room.message", {"msgtype": "m.text", "body": f"Keywords updated for {checker_type} checker: {new_keywords}"})

def find_user_config_by_sender(sender):
    for user in config["users"]:
        if user["matrix_user_id"] == sender:
            return user
    return None

def find_checker_config(user_config, checker_type):
    for checker_config in user_config["checkers"]:
        if checker_config["checker_type"] == checker_type:
            return checker_config
    return None

