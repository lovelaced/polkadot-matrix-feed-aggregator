# Discourse Keyword Matrix Bot

This bot scans a Discourse forum for configured keywords using the Discourse API and posts the results to a Matrix room. The bot continuously checks for new posts containing the keywords and saves its state to allow resuming from the last check.

## Installation

1. Clone the repository or download the source code.

2. Create a virtual environment (optional but recommended):

`python -m venv venv`


3. Activate the virtual environment:

- On Windows:

  ```
  venv\Scripts\activate
  ```

- On macOS and Linux:

  ```
  source venv/bin/activate
  ```

4. Install the required packages:

`pip install -r requirements.txt`


## Configuration

1. Create a `.env` file in the same directory as the script and add your configuration variables:

```
MATRIX_HOMESERVER=https://matrix.org
MATRIX_USER_ID=@bot_user_id:matrix.org
MATRIX_ACCESS_TOKEN=bot_matrix_access_token
MATRIX_ROOM_ID=your_matrix_room_id
DISCOURSE_URL=https://your-discourse-forum-url.com
DISCOURSE_API_KEY=your_discourse_api_key
DISCOURSE_API_USER=your_discourse_api_username
KEYWORDS=keyword1,keyword2,keyword3
CHECK_INTERVAL=60
```


Replace the placeholders with your actual Matrix homeserver URL, access token, room ID, Discourse forum URL, API key, API username, keywords, and check interval.

## Usage

1. Run the script:

`python matrix_discourse_bot.py`


The bot will start running and post new results to the Matrix room when someone creates a new post with any of the configured keywords.

