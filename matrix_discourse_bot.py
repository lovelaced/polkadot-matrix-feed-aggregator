import os
import json
import requests
import asyncio
from datetime import datetime, timedelta
from nio import AsyncClient, RoomMessageText, MatrixRoom
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("matrix-discourse-bot")

# Load environment variables
load_dotenv()
MATRIX_HOMESERVER = os.getenv("MATRIX_HOMESERVER")
MATRIX_USER_ID = os.getenv("MATRIX_USER_ID")
MATRIX_ACCESS_TOKEN = os.getenv("MATRIX_ACCESS_TOKEN")
MATRIX_ROOM_ID = os.getenv("MATRIX_ROOM_ID")
DISCOURSE_URL = os.getenv("DISCOURSE_URL")
DISCOURSE_API_KEY = os.getenv("DISCOURSE_API_KEY")
DISCOURSE_API_USER = os.getenv("DISCOURSE_API_USER")
KEYWORDS = os.getenv("KEYWORDS").split(",")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL"))

LAST_CHECK_FILE = "last_check.txt"

def read_last_check():
    if os.path.isfile(LAST_CHECK_FILE):
        with open(LAST_CHECK_FILE, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    return datetime.now() - timedelta(minutes=1)

def write_last_check(timestamp):
    with open(LAST_CHECK_FILE, "w") as f:
        f.write(timestamp.isoformat())

last_check = read_last_check()

async def on_message(room, event):
    pass

async def check_new_posts():
    global last_check
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        try:
            for keyword in KEYWORDS:
                logger.debug(f"Checking for keyword '{keyword}'")
                await search_discourse_posts(keyword)
            last_check = datetime.now()
            write_last_check(last_check)
            logger.debug(f"Last check timestamp updated to {last_check}")
        except Exception as e:
            logger.error(f"Error while checking for new posts: {str(e)}")

async def search_discourse_posts(keyword):
    url = f"{DISCOURSE_URL}/search.json"
    headers = {
        "Api-Key": DISCOURSE_API_KEY,
        "Api-Username": DISCOURSE_API_USER,
        "Content-Type": "application/json",
    }
    data = {
        "q": f"{keyword} after:{last_check.strftime('%Y-%m-%d')} in:open",
    }

    response = requests.get(url, headers=headers, params=data)
    if response.status_code == 200:
        results = response.json()
        posts = results["posts"]

        if posts:
            logger.info(f"Found {len(posts)} new post(s) with the keyword '{keyword}' since {last_check}")
            for post in posts:
                post_abstract = post['blurb'][:250] + "..." if len(post['blurb']) > 250 else post['blurb']
                post_link = f"{DISCOURSE_URL}/t/{post['topic_id']}/{post['post_number']}"
                formatted_message = f"<strong>{post['username']}</strong> - {post_abstract}<br><a href='{post_link}'>Read more</a>"
                await client.room_send(
                    MATRIX_ROOM_ID,
                    "m.room.message",
                    {
                        "msgtype": "m.text",
                        "format": "org.matrix.custom.html",
                        "formatted_body": formatted_message,
                        "body": f"{post['username']} - {post_abstract}\n{post_link}"
                    }
                )
                logger.debug(f"Posted new message to Matrix room: {post['username']} - {post_link}")
        else:
            logger.debug(f"No new posts found with the keyword '{keyword}' since {last_check}.")
    else:
        logger.error("Failed to fetch search results from Discourse.")

async def main():
    global client
    client = AsyncClient(MATRIX_HOMESERVER)

    # Set access token, user ID, and device ID directly
    client.access_token = MATRIX_ACCESS_TOKEN
    client.user_id = MATRIX_USER_ID
    client.device_id = "AAAAAAAAAA"

    logger.info("Bot started and connected to Matrix homeserver")

    client.add_event_callback(on_message, RoomMessageText)

    # Run check_new_posts as a background task
    asyncio.create_task(check_new_posts())

    await client.sync_forever(timeout=30000)  # Synchronize every 30 seconds

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
