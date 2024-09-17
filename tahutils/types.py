from typing import Any, Union, Optional
from enum import Enum
from datetime import datetime

from tahutils.tahu import sparkplug_b as spb

MetricName = Union[str, Enum]
MetricValues = dict[MetricName, Any]
Time = Union[int, datetime]
MetricTimes = dict[MetricName, Time]

def create_class_from_data_type(data_type_class, output_class_name):
    # Create a dictionary to store the nested classes
    class_dict = {}

    # Iterate through the attributes of the input class
    for attr_name, attr_value in data_type_class.__dict__.items():
        if not attr_name.startswith("__") and isinstance(attr_value, int):
            # Define the inner class with the code attribute
            inner_class = type(attr_name, (object,), {'code': attr_value})
            # Add the inner class to the dictionary with the same name
            class_dict[attr_name] = inner_class

    # Create the outer class dynamically
    return type(output_class_name, (object,), class_dict)

	