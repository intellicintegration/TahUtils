from datetime import datetime
from enum import Enum
from typing import Any

from tahutils.types import MetricName, MetricTimes, Time


def flatten_data_dict(data: dict[str, Any], convert_enum_keys: bool = True, delimiter: str ="/") -> dict[str, Any]:
	"""Flattens nested data dictionaries by joining string keys in nested dicts with the delimiter
	For example:
		flatten_data_dict({'a': {'1': 1, '2': 2}, 'b': 3})
		->
		{'a/1': 1, 'a/2': 2, 'b': 3}
	
	"""
	flat = {}
	for root_key, subtree in data.items():
		if isinstance(root_key, Enum) and convert_enum_keys:
			root_key = root_key.value

		if isinstance(subtree, dict):
			flattened_subtree = flatten_data_dict(subtree)
			flat.update({
				f"{root_key}{delimiter}{sub_key}": sub_value
				for sub_key, sub_value in flattened_subtree.items()
			})
		else:
			flat[root_key] = subtree
	return flat

def process_times(times: MetricTimes) -> dict[str, int]:
	"""Processes the times dictionary to convert to milliseconds"""
	r = {
		metric: int(time.timestamp() * 1000) if isinstance(time, datetime) else time
		for metric, time in times.items()
	}
	return r

def convert_enum_keys(d: dict[MetricName, Time]) -> dict[str, Any]:
	"""Converts the keys of the dictionary to strings if they are enums, otherwise leaves them as is. This is used to convert enum keys to strings for use in the SpbBodel."""
	r = {
		k if isinstance(k, str) else k.value: v
		for k, v in d.items()
	}
	return r