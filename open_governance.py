import yaml
import json
import requests
import os
import logging
from typing import Union, Any
from utils.data_processing import CacheManager
from substrateinterface import SubstrateInterface


class OpenGovernance2:
    def __init__(self, substrate_wss, network, logger):
        self.util = CacheManager
        self.substrate = SubstrateInterface(
            url=substrate_wss,
            ss58_format=2,
            type_registry_preset='kusama'
        )
        self.network = network
        self.logger = logger
        self.logger.debug("OpenGovernance2 initialized")

    def referendumInfoFor(self, index=None):
        """
        Get information regarding a specific referendum or all ongoing referendums.

        :param index: (optional) index of the specific referendum
        :return: dictionary containing the information of the specific referendum or a dictionary of all ongoing referendums
        :raises: ValueError if `index` is not None and not a valid index of any referendum
        """
        self.logger.debug("Fetching referendum info for index: %s", index)
        
        referendum = {}
        if index is not None:
            info = self.substrate.query(
                module='Referenda',
                storage_function='ReferendumInfoFor',
                params=[index]).serialize()
            self.logger.debug("Referendum info for index %s: %s", index, info)
            return info
        else:
            qmap = self.substrate.query_map(
                module='Referenda',
                storage_function='ReferendumInfoFor',
                params=[])
            for index, info in qmap:
                if 'Ongoing' in info:
                    referendum.update({int(index.value): info.value})

            sort = json.dumps(referendum, sort_keys=True)
            data = json.loads(sort)

            #self.logger.debug("All ongoing referendums info: %s", data)
            return data

    def fetch_referendum_data(self, referendum_id: int, network: str) -> Union[str, Any]:
        """
        Fetch the on-chain and Polkassembly data of a referendum using its ID.

        :param referendum_id: ID of the referendum
        :param network: Network name (e.g., 'kusama')
        :return: Dictionary containing the referendum data, or an error message if the data could not be retrieved
        """
        self.logger.debug("Fetching referendum data for ID: %s, network: %s", referendum_id, network)
        
        urls = [
            f"https://api.polkassembly.io/api/v1/posts/on-chain-post?postId={referendum_id}&proposalType=referendums_v2",
            f"https://kusama.subsquare.io/api/gov2/referendums/{referendum_id}",
        ]

        headers = {"x-network": network}
        successful_response = None
        successful_url = None

        for url in urls:
            self.logger.debug("Trying URL: %s", url)
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                json_response = response.json()
                self.logger.debug("Received response from URL: %s, response: %s", url, json_response)

                if "title" not in json_response.keys():
                    json_response["title"] = "None"

                if json_response["title"] is None:
                    return {"title": "None",
                            "content": "Unable to retrieve details from both sources",
                            "successful_url": None}

                if successful_response is None:
                    successful_response = json_response
                    successful_url = url

            except requests.exceptions.HTTPError as http_error:
                self.logger.error("HTTP exception occurred: %s", http_error)
                raise f"HTTP exception occurred: {http_error}"

        if successful_response is not None and successful_response["title"] == "None":
            return {"title": "None",
                    "content": "Unable to retrieve details from both sources",
                    "successful_url": None}
        else:
            successful_response["successful_url"] = successful_url
            self.logger.debug("Returning successful response: %s", successful_response)
            return successful_response

    def time_until_block(self, target_block: int) -> int:
        """
        Calculate the estimated time in minutes until the specified target block is reached on the Kusama network.

        Args:
            target_block (int): The target block number for which the remaining time needs to be calculated.

        Returns:
            int: The estimated time remaining in minutes until the target block is reached. If the target block has
            already been reached, the function will return None.
    
        Raises:
            Exception: If any error occurs while trying to calculate the time remaining until the target block.
        """
        try:
            # Get the current block number
            current_block = self.substrate.get_block_number(block_hash=self.substrate.block_hash)
            if target_block <= current_block:
                print("The target block has already been reached.")
                return False
    
            # Calculate the difference in blocks
            block_difference = target_block - current_block
    
            # Get the average block time (6 seconds for Kusama)
            avg_block_time = 6
    
            # Calculate the remaining time in seconds
            remaining_time = block_difference * avg_block_time
    
            # Convert seconds to minutes
            minutes = remaining_time / 60
    
            return int(minutes)
    
        except Exception as error:
            print(f"An error occurred while trying to calculate the remaining time until {target_block} is met... {error}")

    def search_keywords(text, keywords):
        self.logger.debug("Checking referendums for keywords: %s", keywords)
        return any(keyword.lower() in text.lower() for keyword in keywords)

    def check_referendums(self, keywords):
        """
        Check the referendums and return any new referendums containing specific keywords as a JSON string.

        The method retrieves the information about referendums using the `referendumInfoFor` method and
        caches the result using the `cache_difference` method from the `util` attribute of the `self` object.

        If there are any new referendums, the method retrieves the on-chain and polkassembly information about
        each new referendum and adds it to a dictionary. The dictionary is then filtered by the keywords and
        returned as a JSON string.

        Returns:
            str: The new referendums containing specific keywords as a JSON string or False if there are no new referendums.
        """
        new_referenda = {}

        referendum_info = self.referendumInfoFor()

        #self.logger.debug("Referendum Info: %s", json.dumps(referendum_info, indent=2))

        cache_file_path = os.path.join(os.path.dirname(__file__), 'data', 'governance.cache')

        results = self.util.get_cache_difference(filename=cache_file_path, data=referendum_info)
        self.util.save_data_to_cache(filename=cache_file_path, data=referendum_info)
        self.logger.debug("Received results")

        if results:
            self.logger.debug("New referendums found: %s", json.dumps(results, indent=2))
            for key, value in results.items():
                if 'added' in key:
                    for index in results['dictionary_item_added']:
                        index = index.strip('root').replace("['", "").replace("']", "")
                        onchain_info = referendum_info[index]['Ongoing']
                        polkassembly_info = self.fetch_referendum_data(referendum_id=index, network=config['network'])
                        self.logger.debug("Polkassembly info: %s, index: %s, onchain info: %s", polkassembly_info, index, onchain_info)

                        new_referenda.update({
                            f"{index}": polkassembly_info
                        })

                        new_referenda[index]['onchain'] = onchain_info

            #self.logger.debug("New referendums with details: %s", json.dumps(new_referenda, indent=2))

            # Filter the new referendums based on the keywords
            filtered_referenda = {}
            for index, referendum_data in new_referenda.items():
                title = referendum_data.get('title', '')
                content = referendum_data.get('content', '')

                if self.search_keywords(title, keywords) or self.search_keywords(content, keywords):
                    filtered_referenda[index] = referendum_data

            self.logger.debug("Filtered referendums based on keywords: %s", json.dumps(filtered_referenda, indent=2))
            return filtered_referenda

        return {} 
