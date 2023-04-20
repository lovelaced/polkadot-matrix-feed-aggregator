from open_governance import OpenGovernance2
from data_checker import DataChecker

class GovernanceChecker(DataChecker):
    def __init__(self, client, matrix_room_id, checker_config, logger):
        super().__init__(client, matrix_room_id, checker_config, logger)
        self.substrate_wss = checker_config["substrate_wss"]
        self.network = checker_config["network"]
        self.keywords = checker_config["keywords"]
        self.open_governance = OpenGovernance2(self.substrate_wss, self.network, logger)

    async def check_new_data(self):
        self.logger.debug("Checking new data for GovernanceChecker")
        new_referendums = self.open_governance.check_referendums(self.keywords)

        if new_referendums:
            self.logger.debug(f"Found {len(filtered_referendums)} new referendums")
            for index, referendum_info in filtered_referendums.items():
                title = referendum_info["title"]
                url = referendum_info["successful_url"]
                message = f"New Governance Referendum: {title}\nReferendum ID: {index}\nURL: {url}"
                await self.client.room_send(
                    self.matrix_room_id,
                    "m.room.message",
                    {
                        "msgtype": "m.text",
                        "body": message
                    }
                )
                self.logger.debug(f"Posted new referendum message to Matrix room: {title} - {url}")
        else:
            self.logger.debug("No new referendums found")
