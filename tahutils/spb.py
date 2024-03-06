from tahutils.tahu import sparkplug_b as spb
from typing import Any, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

COMMAND_METRICS = {
	"Node Control/Next Server", 
	"Node Control/Rebirth", 
	"Node Control/Reboot"
}

MetricName = Union[str, Enum]
MetricValues = dict[MetricName, Any]
Time = Union[int, datetime]
MetricTimes = dict[MetricName, Time]

def process_times(times: MetricTimes) -> dict[str, int]:
	"""Processes the times dictionary to convert to milliseconds"""
	r = {
		metric: int(time.timestamp() * 1000) if isinstance(time, datetime) else time
		for metric, time in times.items()
	}
	return r

def convert_enum_keys(d: dict[MetricName, Any]) -> dict[str, Any]:
	"""Processes the times dictionary to convert to milliseconds"""
	r = {
		k if isinstance(k, str) else k.value: v
		for k, v in d.items()
	}
	return r

class SpbModel:
	def __init__(
			self, 
			metrics: dict[MetricName, spb.MetricDataType], 
			use_aliases: bool=False, 
			auto_serialize: bool=True
		) -> None:
		metrics = convert_enum_keys(metrics)
		self.metrics = set(metrics.keys())
		self.metric_types = {k:v for k,v in metrics.items()}

		self.last_published = {}

		self._use_aliases = use_aliases
		self.all_metrics = COMMAND_METRICS | self.metrics
		self.alias = {metric: i for i, metric in enumerate(self.all_metrics)} \
			if self._use_aliases else \
			{metric: None for metric in self.all_metrics}
		
		self._alias_to_metric = {i: metric for i, metric in self.alias.items()} \
			if self._use_aliases else None

		self.auto_serialize = auto_serialize

		self.node_death_requested = False

	@property
	def aliasing(self) -> bool:
		"""Returns whether aliases are being used"""
		return self._use_aliases

	def aliasToMetric(self, alias: int) -> str:
		"""Returns the metric for the given alias. Raises a ValueError if aliases are not being used."""
		if not self._use_aliases:
			raise ValueError("Aliases are not being used")
		return self._alias_to_metric[alias]
	
	def metricToAlias(self, metric: str) -> int:
		"""Returns the alias for the given metric. Raises a ValueError if aliases are not being used."""
		if not self._use_aliases:
			raise ValueError("Aliases are not being used")
		return self.alias[metric]
	
	def _serialize(self, p: spb.Payload) -> Union[bytes, spb.Payload]:
		"""Serializes the payload if auto_serialize is True, otherwise is a no-op."""
		if self.auto_serialize:
			return bytes(p.SerializeToString())
		return p
	
	def getNodeDeathPayload(self):
		"""Returns a death payload for the node. This must be requested and sent as part of the connection."""
		self.node_death_requested = True
		return self._serialize(spb.getNodeDeathPayload())

	def getNodeBirthPayload(self, state: MetricValues, times: MetricTimes = dict()):
		"""Returns a birth payload for the given state. State must be set for all metrics."""
		state = convert_enum_keys(state)
		times = convert_enum_keys(times)
		
		if not self.node_death_requested:
			raise ValueError("Must request death before requesting new birth")
		if set(COMMAND_METRICS | state.keys()) != set(self.all_metrics):
			print(state.keys(), self.all_metrics)
			raise ValueError("Node birth metrics must be the same as the model's metrics")

		times = process_times(times)

		payload = spb.getNodeBirthPayload()

		for metric in COMMAND_METRICS:
			spb.addMetric(payload, metric, self.alias[metric], spb.MetricDataType.Boolean, False)

		for metric, value in state.items():
			mt = self.metric_types[metric]

			self.last_published[metric] = value

			if metric in times:
				spb.addMetric(payload, metric, self.alias[metric], mt, value, metric[times])
			else:
				spb.addMetric(payload, metric, self.alias[metric], mt, value)

		return self._serialize(payload)
	
	def getDataPayload(self, state: MetricValues, times: MetricTimes = dict()):
		"""Returns a data payload for the given state"""
		state = convert_enum_keys(state)
		times = convert_enum_keys(times)
		
		if not set(state.keys()).issubset(set(self.all_metrics)):
			raise ValueError("Node data metrics must be a subset of the model's metrics")
		
		times = process_times(times)

		payload = spb.getDdataPayload()

		for metric, value in state.items():
			if value != self.last_published.get(metric, ...):
				mt = self.metric_types[metric]
				self.last_published[metric] = value
			
				if metric in times:
					spb.addMetric(payload, metric, self.alias[metric], mt, value, times[metric])
				else:
					spb.addMetric(payload, metric, self.alias[metric], mt, value)

		return self._serialize(payload)

@dataclass
class SpbTopic:
	group_id: str
	edge_node_id: str

	device_id: str | None = None

	namespace: str = "spBv1.0"

	def construct(self, mtype: str):
		mtype = mtype.upper()
		if self.device_id:
			return f"{self.namespace}/{self.group_id}/{mtype}/{self.edge_node_id}/{self.device_id}"
		return f"{self.namespace}/{self.group_id}/{mtype}/{self.edge_node_id}"

	@property
	def nbirth(self):
		return self.construct("nbirth")
	
	@property
	def ndeath(self):
		return self.construct("ndeath")
	
	@property
	def dbirth(self):
		return self.construct("dbirth")
	
	@property
	def ddeath(self):
		return self.construct("ddeath")
	
	@property
	def ndata(self):
		return self.construct("ndata")
	
	@property
	def ddata(self):
		return self.construct("ddata")
	
	@property
	def ncmd(self):
		return self.construct("ncmd")
	
	@property
	def dcmd(self):
		return self.construct("dcmd")
	
	@property
	def state(self):
		return self.construct("state")
	
	