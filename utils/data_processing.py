import os
import json
from typing import Dict, Any
import deepdiff


class CacheManager:
    @staticmethod
    def save_data_to_cache(filename: str, data: Dict[str, Any]) -> None:
        """Save data to a JSON file."""
        with open(filename, 'w') as cache:
            json.dump(data, cache, indent=4)

    @staticmethod
    def load_data_from_cache(filename: str) -> Dict[str, Any]:
        """Load data from a JSON file."""
        if not os.path.isfile(filename):
            return {}

        with open(filename, 'r') as cache:
            cached_file = json.load(cache)

        return cached_file

    @staticmethod
    def get_cache_difference(filename: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare the provided data with the cached data and return the difference using deepdiff."""

        if not os.path.isfile(filename):
            CacheManager.save_data_to_cache(filename, data)
            return {}

        with open(filename, 'r') as cache_file:
            cached_data = json.load(cache_file)

        difference = deepdiff.DeepDiff(cached_data, data, ignore_order=True).to_dict()
        return difference or {}

