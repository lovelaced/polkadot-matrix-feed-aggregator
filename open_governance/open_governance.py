import yaml
import json
import requests
import os
import logging
from typing import Union, Any, List, Dict
from substrateinterface import SubstrateInterface
from datetime import datetime


class OpenGovernance2:
    def __init__(self, substrate_wss, network, logger):
        self.network = network
        self.substrate = SubstrateInterface(
            url=substrate_wss,
            ss58_format=2,
            type_registry_preset=self.network
        )
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
            self.logger.debug("Some data here: %s", sort)
            data = json.loads(sort)

            return data

    def fetch_all_referendum_data(self, network: str, last_check: datetime) -> List[Dict[str, Any]]:
        page = 1
        page_size = 100
        all_referenda = []
    
        while True:
            url = f"https://{self.network}.subsquare.io/api/gov2/referendums?page={page}&pageSize={page_size}"
            headers = {"x-network": network}
    
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                json_response = response.json()
                self.logger.debug("Trying to get info from %s", url)
                referenda = json_response["items"]
                total = json_response["total"]
    
                if not referenda:
                    break
    
                for referendum in referenda:
                    #self.logger.debug("JSON response: %s", json.dumps(referendum, indent=2))
                    created_at = datetime.strptime(referendum['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if created_at < last_check:
                        return all_referenda
    
                    index = str(referendum["referendumIndex"])
                    polkassembly_url = f"https://api.polkassembly.io/api/v1/posts/on-chain-post?postId={index}&proposalType=referendums_v2"
                    polkassembly_info = self.fetch_referendum_data(referendum_id=index, network=self.network, url=polkassembly_url)
    
                    if polkassembly_info:
                        referendum.update(polkassembly_info)
    
                    all_referenda.append(referendum)
    
                if len(all_referenda) >= total:
                    break
    
                page += 1
    
            except requests.exceptions.HTTPError as http_error:
                self.logger.error("HTTP exception occurred: %s", http_error)
                raise Exception(f"HTTP exception occurred: {http_error}")
    
        return all_referenda

    def fetch_referendum_data(self, referendum_id: int, network: str, url: str) -> Union[str, Any]:
        self.logger.debug("Fetching referendum data for ID: %s, network: %s", referendum_id, network)
    
        headers = {"x-network": network}
    
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            json_response = response.json()
    
            if "title" not in json_response.keys():
                json_response["title"] = "None"
    
            if json_response["title"] is None:
                return {"title": "None",
                        "content": "Unable to retrieve details from both sources"}
    
            return json_response
    
        except requests.exceptions.HTTPError as http_error:
            self.logger.error("HTTP exception occurred: %s", http_error)
            raise f"HTTP exception occurred: {http_error}"
    
    def time_until_block(self, target_block: int) -> int:
        """
        Calculate the estimated time in minutes until the specified target block is reached on the network.

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
    
            # Get the average block time (6 seconds)
            avg_block_time = 6
    
            # Calculate the remaining time in seconds
            remaining_time = block_difference * avg_block_time
    
            # Convert seconds to minutes
            minutes = remaining_time / 60
    
            return int(minutes)
    
        except Exception as error:
            print(f"An error occurred while trying to calculate the remaining time until {target_block} is met... {error}")

    def search_keywords(self, text, keywords):
        for keyword in keywords:
            if keyword.lower() in text.lower():
                return keyword
        return None

        return any(keyword.lower() in text.lower() for keyword in keywords)

    def check_referendums(self, keywords, last_check):
        all_referenda = self.fetch_all_referendum_data(network=self.network, last_check=last_check)
        new_referenda = {}
    
        for referendum in all_referenda:
            index = str(referendum["referendumIndex"])
            created_at = datetime.strptime(referendum.get('createdAt', ''), "%Y-%m-%dT%H:%M:%S.%fZ")
            #self.logger.debug("Referendum created at: %s", created_at)
    
            if created_at > last_check:
                self.logger.debug("Found a new referendum")
                new_referenda[index] = referendum
            else:
                self.logger.debug("Referendum is not new: %s is older than %s", created_at, last_check)

        self.logger.debug("Checking %s referendums for keywords: %s", len(new_referenda.keys()), keywords)
        filtered_referenda = {} 
        for index, referendum_data in new_referenda.items():
            title = referendum_data.get('title', '')
            content = referendum_data.get('content', '')
        
            title_match = self.search_keywords(title, keywords)
            content_match = self.search_keywords(content, keywords)
        
            if title_match or content_match:
                matched_keyword = title_match or content_match
                successful_url = f"https://{self.network}.subsquare.io/referenda/referendum/{index}"
                referendum_data["successful_url"] = successful_url
                referendum_data["matched_keyword"] = matched_keyword
                referendum_data["content"] = content
                filtered_referenda[index] = referendum_data
    
        return filtered_referenda
    
