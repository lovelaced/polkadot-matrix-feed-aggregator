from open_governance.open_governance import OpenGovernance2
from data_checkers import DataChecker
import markdown

class GovernanceChecker(DataChecker):
    def __init__(self, client, matrix_room_id, checker_config, logger, last_check):
        super().__init__(client, matrix_room_id, checker_config, logger)
        self.substrate_wss = checker_config["substrate_wss"]
        self.network = checker_config["network"]
        self.keywords = checker_config["keywords"]
        self.last_check = last_check
        self.open_governance = OpenGovernance2(self.substrate_wss, self.network, logger)

    async def check_new_data(self):
        self.logger.debug("Checking new data for GovernanceChecker")
        new_referendums = self.open_governance.check_referendums(self.keywords, self.last_check)
    
        if new_referendums:
            self.logger.debug(f"Found {len(new_referendums)} new referendums")
            for index, referendum_info in new_referendums.items():
                title = referendum_info["title"]
                url = referendum_info["successful_url"]
                matched_keyword = referendum_info["matched_keyword"]
                content_blurb = referendum_info["content"][:250] + "..." if len(referendum_info["content"]) > 250 else referendum_info["content"]
    
                # Convert mixed content to HTML
                content_blurb_html = markdown.markdown(content_blurb)
    
                plain_text_message = f"New Governance Referendum: {title}\nMatched keyword: {matched_keyword}\nContent: {content_blurb}\nReferendum ID: {index}\nURL: {url}"
                html_message = f"<strong>New Governance Referendum:</strong> {title}<br>Matched keyword: {matched_keyword}<br>Content: {content_blurb_html}<br>Referendum ID: {index}<br>URL: {url}"
    
                await self.client.room_send(
                    self.matrix_room_id,
                    "m.room.message",
                    {
                        "msgtype": "m.text",
                        "format": "org.matrix.custom.html",
                        "formatted_body": html_message,
                        "body": plain_text_message
                    }
                )
                self.logger.debug(f"Posted new referendum message to Matrix room: {title} - {url}")
        else:
            self.logger.debug("No new referendums found")
