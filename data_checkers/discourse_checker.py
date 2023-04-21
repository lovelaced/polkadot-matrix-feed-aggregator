# data_checkers/discourse_checker.py

import requests
from datetime import datetime
from data_checkers import DataChecker

class DiscourseChecker(DataChecker):
    def __init__(self, client, matrix_room_id, checker_config, logger, last_check):
        super().__init__(client, matrix_room_id, checker_config, logger)
        self.discourse_url = checker_config["discourse_url"]
        self.discourse_api_key = checker_config["discourse_api_key"]
        self.discourse_api_user = checker_config["discourse_api_user"]
        self.keywords = checker_config["keywords"]
        self.last_check = last_check

    async def check_new_data(self):
        self.logger.debug("Checking new data for DiscourseChecker")
        for keyword in self.keywords:
            await self.search_discourse_posts(keyword)

    async def search_discourse_posts(self, keyword):
        self.logger.debug(f"Searching {self.discourse_url} posts for keyword: {keyword}")
        url = f"{self.discourse_url}/search.json"
        headers = {
            "Api-Key": self.discourse_api_key,
            "Api-Username": self.discourse_api_user,
            "Content-Type": "application/json",
        }
        data = {
                "q": f"{keyword} after:{self.last_check.strftime('%Y-%m-%d')} in:open",
        }
    
        req = requests.Request('GET', url, headers=headers, params=data)
        prepared_req = req.prepare()
    
        self.logger.debug(f"Search URL: {prepared_req.url}")
    
        response = requests.get(url, headers=headers, params=data)
        if response.status_code == 200:
            results = response.json()
            posts = results["posts"]
            self.logger.debug(f"Posts: {posts}")
    
            if posts:
                self.logger.debug(f"Found {len(posts)} new posts with keyword: {keyword}")
                for post in posts:
                    post_abstract = post['blurb'][:250] + "..." if len(post['blurb']) > 250 else post['blurb']
                    post_link = f"{self.discourse_url}/t/{post['topic_id']}/{post['post_number']}"
                    formatted_message = f"🔍 <strong>Discourse ({self.discourse_url}, {keyword})</strong><br><strong>{post['username']}</strong> - {post_abstract}<br><a href='{post_link}'>Read more</a>"
                    self.logger.debug(f"Sending post to Matrix room: {post_link}")
    
                    try:
                        response = await self.client.room_send(
                            self.matrix_room_id,
                            "m.room.message",
                            {
                                "msgtype": "m.text",
                                "format": "org.matrix.custom.html",
                                "formatted_body": formatted_message,
                                "body": f"{post['username']} - {post_abstract}\n{post_link}"
                            }
                        )
                        #self.logger.debug(f"Matrix room_send response: {response}")
                    except Exception as e:
                        self.logger.error(f"Failed to send message to Matrix room: {str(e)}")
        else:
            self.logger.error("Failed to fetch search results from Discourse.")
    
