# stack_exchange_checker.py
import requests
from data_checkers import DataChecker

class StackExchangeChecker(DataChecker):
    def __init__(self, client, matrix_room_id, checker_config, logger, last_check):
        super().__init__(client, matrix_room_id, checker_config, logger)
        self.stack_exchange_site = checker_config["stack_exchange_site"]
        self.stack_exchange_api_key = checker_config["stack_exchange_api_key"]
        self.keywords = checker_config["keywords"]
        self.last_check = last_check

    async def check_new_data(self):
        self.logger.debug("Checking new data for StackExchangeChecker")
        for keyword in self.keywords:
            await self.search_stack_exchange_posts(keyword)

    async def search_stack_exchange_posts(self, keyword):
        self.logger.debug(f"Searching {self.stack_exchange_site} posts for keyword: {keyword}")
        url = f"https://api.stackexchange.com/2.3/search/advanced"
        params = {
            "key": self.stack_exchange_api_key,
            "site": self.stack_exchange_site,
            "sort": "creation",
            "q": keyword,
            "fromdate": int(self.last_check.timestamp()),
            "filter": "withbody"
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json()
            posts = results["items"]

            if posts:
                self.logger.debug(f"Found {len(posts)} new posts with keyword: {keyword}")
                for post in posts:
                    post_abstract = post['title'][:250] + "..." if len(post['title']) > 250 else post['title']
                    post_link = post['link']
                    formatted_message = f"🔍 <strong>Stack Exchange ({keyword})</strong><br><strong>{post['owner']['display_name']}</strong> - {post_abstract}<br><a href='{post_link}'>Read more</a>"
                    self.logger.debug(f"Sending SE post to Matrix room: {post_link}")

                    try:
                        response = await self.client.room_send(
                            self.matrix_room_id,
                            "m.room.message",
                            {
                                "msgtype": "m.text",
                                "format": "org.matrix.custom.html",
                                "formatted_body": formatted_message,
                                "body": f"{post['owner']['display_name']} - {post_abstract}\n{post_link}"
                            }
                        )
                        #self.logger.debug(f"Matrix room_send response: {response}")
                    except Exception as e:
                        self.logger.error(f"Failed to send message to Matrix room: {str(e)}")
        else:
            self.logger.error("Failed to fetch search results from Stack Exchange.")

