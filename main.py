import asyncio
from dotenv import load_dotenv

from matrix_client import setup_matrix_client, handle_set_keywords
from discourse_checker import DiscourseChecker
from governance_checker import GovernanceChecker
from utils.utils import load_config, read_last_check, write_last_check
from logger_setup import setup_logger

logger = setup_logger()

config = load_config()

checker_classes = {
    "discourse": DiscourseChecker,
    "governance": GovernanceChecker,
}

async def main():
    global client
    client = await setup_matrix_client(config)
    logger.info("Bot started and connected to Matrix homeserver")

    while True:
        await asyncio.sleep(config["global_check_interval"])
        logger.debug("Woke up from sleep, checking for new data")
        try:
            for user in config["users"]:
                user_name = user["name"]
                matrix_room_id = user["matrix_room_id"]
                logger.debug(f"Checking data for user: {user_name}")
                for checker_config in user["checkers"]:
                    checker_type = checker_config["checker_type"]
                    checker_class = checker_classes.get(checker_type)
                    if checker_class:
                        logger.debug(f"Running checker of type: {checker_type}")
                        last_check = read_last_check(user_name, checker_type, logger)
                        if checker_type == "discourse":
                            for forum_config in checker_config["forums"]:
                                checker = checker_class(client, matrix_room_id, forum_config, logger, last_check)
                                await checker.check_new_data()
                        else:
                            checker = checker_class(client, matrix_room_id, checker_config, logger, last_check)
                            await checker.check_new_data()
                        write_last_check(user_name, checker_type, logger)
                    else:
                        logger.error(f"Unknown checker_type: {checker_type}")
        except Exception as e:
            logger.error(f"Error while checking for new data: {str(e)}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

