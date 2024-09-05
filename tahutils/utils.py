from datetime import datetime
from enum import Enum
from typing import Any, Annotated, get_origin, get_args

from tahutils.types import MetricName, MetricTimes, Time

from dataclasses import dataclass, is_dataclass, fields


def make_key(*args: Enum, delimiter: str = "/") -> str:
	l = [e.value if isinstance(e, Enum) else e for e in args]
	return delimiter.join(l)

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

def dataclass_to_dict(cls) -> dict[str, Any]:
	if not is_dataclass(cls):
		raise ValueError(f"{cls} is not a dataclass")
	
	result = {}
	for field in fields(cls):
		field_name, field_type = field.name, field.type
		if get_origin(field_type) is Annotated:
			field_type, *metadata = get_args(field_type)
			field_name = metadata[0]
		if is_dataclass(field_type):
			result[field_name] = dataclass_to_dict(field_type)
		else:
			result[field_name] = field_type

	return result

def instance_to_dict(instance) -> dict[str, Any]:
	if not is_dataclass(instance):
		raise ValueError(f"{instance} is not a dataclass instance")
	
	result = {}
	for field in fields(instance):
		field_name, field_value = field.name, getattr(instance, field.name)
		field_type = field.type
		
		# Handle Annotated types
		if get_origin(field_type) is Annotated:
			field_type, *metadata = get_args(field_type)
			field_name = metadata[0]  # Assuming the first metadata argument is the desired field name
		
		# Recursively convert nested dataclasses
		if field_value is ...:
			pass
		elif is_dataclass(field_value):
			result[field_name] = instance_to_dict(field_value)
		else:
			result[field_name] = field_value

	return result