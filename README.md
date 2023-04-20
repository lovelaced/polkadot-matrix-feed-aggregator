# Polkadot Feed Bot for Matrix

## Overview

This project is an information monitoring bot for Matrix, which periodically checks different sources, such as Discourse forums, governance platforms, and StackExchange sites, for user-defined keywords. When new content containing a keyword is found, the bot sends a message to a specified Matrix room.

## Prerequisites

- Python 3.7 or higher
- A Matrix account and access token
- API keys and credentials for the data sources you want to monitor (Discourse, governance platforms, StackExchange)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/lovelaced/polkadot-matrix-feed-aggregator.git
cd polkadot-matrix-feed-aggregator
```

    Install the required dependencies:

```bash

pip install -r requirements.txt
```

    Create a config.json file in the project root directory with your desired configuration. Use the provided config_example.json as a template. Replace the placeholders with your actual API keys, Matrix room IDs, and other relevant settings.

    Run the bot:

```bash

python main.py
```

### Usage

    Define the keywords you want to monitor in the config.json file.

    Add the checkers you want to use for each user. Supported checkers are:

    discourse: Monitors Discourse forums.
    governance: Monitors governance platforms.
    stackexchange: Monitors StackExchange sites.

    Configure the checkers with the appropriate settings, such as API keys, URLs, and other required parameters.

    Run the bot, and it will start monitoring the specified sources for the defined keywords. When new content is found, the bot will send a message to the specified Matrix rooms.

### Configuration

See the provided config_example.json for an example configuration. The configuration includes:

    homeserver: The Matrix homeserver URL.
    user_id: The Matrix user ID for the bot.
    access_token: The Matrix access token for the bot.
    global_check_interval: The interval (in seconds) at which the bot checks for new data.
    users: An array of user configurations, including the Matrix room ID, and checkers with their specific settings.

### Contributing

Pull requests and issues are welcome. Please open an issue if you encounter any problems or would like to suggest improvements.
