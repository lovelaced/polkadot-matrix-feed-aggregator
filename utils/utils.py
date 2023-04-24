import json
import os
from datetime import datetime
import time
from typing import Dict
from typing import Optional

def load_config(config_file: str = "config/config.json") -> Dict:
    """
    Load the configuration file as a dictionary.

    Args:
        config_file (str, optional): Path to the JSON configuration file. Defaults to "config.json".

    Returns:
        Dict: A dictionary containing the configuration data.
    """
    with open(config_file, "r") as f:
        config = json.load(f)

    # Replace the sensitive data keys with environment variable names
    for user in config["users"]:
        for checker in user["checkers"]:
            if checker["checker_type"] == "discourse":
                for forum in checker["forums"]:
                    if "discourse_api_key_env" in forum:
                        env_var_name = forum["discourse_api_key_env"]
                        forum["discourse_api_key"] = os.environ[env_var_name]
    return config

def read_last_check(user: str, checker_type: str, logger, last_check_file: str = "data/last_check.json") -> datetime:
    if os.path.exists(last_check_file):
        with open(last_check_file, "r") as f:
            last_check_data = json.load(f)

        key = f"{user}_{checker_type}"
        if key in last_check_data:
            return datetime.fromisoformat(last_check_data[key])

    last_check = datetime.now()
    write_last_check(user, checker_type, logger, last_check_file)
    logger.info(f"Initializing last check for user {user} and checker type {checker_type}.")
    return last_check


def write_last_check(user: str, checker_type: str, logger, last_check_file: str = "data/last_check.json") -> None:
    if os.path.exists(last_check_file):
        with open(last_check_file, "r") as f:
            last_check_data = json.load(f)
    else:
        last_check_data = {}

    key = f"{user}_{checker_type}"
    current_time = datetime.now()
    last_check_data[key] = current_time.isoformat()

    os.makedirs(os.path.dirname(last_check_file), exist_ok=True)
    with open(last_check_file, "w") as f:
        json.dump(last_check_data, f)

    logger.info(f"Updated last check for user {user} and checker type {checker_type} to {current_time}.")

