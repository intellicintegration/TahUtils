from typing import Any, Union, Optional
from enum import Enum
from datetime import datetime

MetricName = Union[str, Enum]
MetricValues = dict[MetricName, Any]
Time = Union[int, datetime]
MetricTimes = dict[MetricName, Time]