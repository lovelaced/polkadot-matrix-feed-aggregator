import json
import os
from datetime import datetime
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
    return config

def read_last_check(user: str, checker_type: str, logger, last_check_file: str = "last_check.json") -> datetime:
    """
    Read the last check timestamp for the given user and checker type from the specified file.

    Args:
        user (str): The user identifier.
        checker_type (str): The checker type identifier.
        last_check_file (str, optional): The path to the file containing the last check data. Defaults to "last_check.json".

    Returns:
        datetime: The last check timestamp as a datetime object.
    """
    if os.path.exists(last_check_file):
        with open(last_check_file, "r") as f:
            last_check_data = json.load(f)

        key = f"{user}_{checker_type}"
        if key in last_check_data:
            return datetime.fromisoformat(last_check_data[key])

    last_check = datetime.now()
    write_last_check(user, checker_type, logger)
    logger.info(f"Initializing last check for user {user} and checker type {checker_type}.")
    return last_check


def write_last_check(user: str, checker_type: str, logger, last_check_file: str = "last_check.json") -> None:
    """
    Write the last check timestamp for the given user and checker type to the specified file.

    Args:
        user (str): The user identifier.
        checker_type (str): The checker type identifier.
        last_check_file (str, optional): The path to the file containing the last check data. Defaults to "last_check.json".
    """
    if os.path.exists(last_check_file):
        with open(last_check_file, "r") as f:
            last_check_data = json.load(f)
    else:
        last_check_data = {}

    key = f"{user}_{checker_type}"
    current_time = datetime.now()  # Get the current time
    last_check_data[key] = current_time.isoformat()

    with open(last_check_file, "w") as f:
        json.dump(last_check_data, f)

    logger.info(f"Updated last check for user {user} and checker type {checker_type} to {current_time}.")

