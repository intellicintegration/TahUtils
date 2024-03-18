from typing import Any


def flatten_data_dict(data: dict[str, Any], delimiter: str ="/") -> dict[str, Any]:
	"""Flattens nested data dictionaries by joining string keys in nested dicts with the delimiter
	For example:
		flatten_data_dict({'a': {'1': 1, '2': 2}, 'b': 3})
		->
		{'a/1': 1, 'a/2': 2, 'b': 3}
	
	"""
	flat = {}
	for root_key, subtree in data.items():
		if isinstance(subtree, dict):
			flattened_subtree = flatten_data_dict(subtree)
			flat.update({
				f"{root_key}{delimiter}{sub_key}": sub_value
				for sub_key, sub_value in flattened_subtree.items()
			})
		else:
			flat[root_key] = subtree
	return flat