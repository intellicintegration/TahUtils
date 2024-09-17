from pathlib import Path
import importlib
import sys
from tahutils.tahu.sparkplug_b import MetricDataType

ROOT_CLASS_NAME = "BaseType"

HEADER = f"""
# The {Path(__file__).name} script can help you generate the class skeletons
from dataclasses import dataclass
from typing import Annotated, get_origin, get_args

from tahutils.tahu.sparkplug_b import MetricDataType


class {ROOT_CLASS_NAME}:
	code = None
	python_type = None

def get_type_code(obj):
	if get_origin(obj) is Annotated:
		dt =  get_args(obj)[0]
	dt = obj
	if isinstance(dt, {ROOT_CLASS_NAME}):
		return dt.code
	return None

"""


CLASS_TEMPLATE = """
class {name}({root_class}):
	code = {value}
	python_type = {python_type}
"""

# TARGET = "tahutils/datatypes.py"

def main():
	print(HEADER, end="")
	for name, value in vars(MetricDataType).items():
		if not name.startswith('_'):
			python_type = None
			if "Int" in name:
				python_type = "int"
			elif name in {"Float", "Double"}:
				python_type = "float"
			elif name == "Boolean":
				python_type = "bool"
			elif name in {"String", "Text", "UUID"}:
				python_type = "str"
			elif name == "Bytes":
				python_type = "bytes"
			elif name == "DateTime":
				python_type = "int"


			print(
				CLASS_TEMPLATE.format(
					name=name, 
					value=f"MetricDataType." + name, 
					root_class=ROOT_CLASS_NAME,
					python_type=python_type
					)
				, end="")

if __name__ == "__main__":
	main()