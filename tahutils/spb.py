from tahutils.tahu import sparkplug_b as spb
from tahutils.utils import flatten_data_dict, process_times, convert_enum_keys
from typing import Optional, Union
from tahutils.types import MetricName, MetricValues, MetricTimes
from enum import Enum
from dataclasses import dataclass
from functools import cached_property

COMMAND_METRICS = {
	"Node Control/Next Server", 
	"Node Control/Rebirth", 
	"Node Control/Reboot"
}

class SpbModel:
	def __init__(
			self, 
			metrics: dict[MetricName, spb.MetricDataType], 
			use_aliases: bool=False, 
			auto_serialize: bool=True,
			serialize_cast: Optional[callable] = bytearray,
			flatten_states: bool=True,
			flattened_dict_delimiter: str = "/"
		) -> None:
		self.flatten_states = flatten_states
		self.flattened_dict_delimiter = flattened_dict_delimiter

		metrics = self._preprocess_dict(metrics)
		self.metrics = set(metrics.keys())
		self.metric_types = {k:v for k,v in metrics.items()} | {m: spb.MetricDataType.Boolean for m in COMMAND_METRICS}

		self.last_published = {}

		self._use_aliases = use_aliases
		self.all_metrics = COMMAND_METRICS | self.metrics
		self._metric_to_alias = {metric: i for i, metric in enumerate(self.all_metrics)} \
			if self._use_aliases else \
			{metric: None for metric in self.all_metrics}
		
		self._alias_to_metric = {i: metric for i, metric in self._metric_to_alias.items()} \
			if self._use_aliases else None

		self.auto_serialize = auto_serialize
		self.serialize_cast = serialize_cast


		self.node_death_requested = False

	@property
	def aliasing(self) -> bool:
		"""Returns whether aliases are being used"""
		return self._use_aliases

	def _preprocess_dict(self, state: MetricValues, is_time: bool = False) -> MetricValues:
		"""Preprocesses the state, flattening it if enabled, and converting enum keys. Can optionally preprocess times."""
		r = flatten_data_dict(state, delimiter=self.flattened_dict_delimiter) if self.flatten_states else convert_enum_keys(state)
		if is_time:
			r = process_times(r)
		return r

	def aliasToMetric(self, alias: int) -> str:
		"""Returns the metric for the given alias. Raises a ValueError if aliases are not being used."""
		if not self._use_aliases:
			raise ValueError("Aliases are not being used")
		return self._alias_to_metric[alias]
	
	def metricToAlias(self, metric: str) -> int:
		"""Returns the alias for the given metric. Raises a ValueError if aliases are not being used."""
		if isinstance(metric, Enum):
			metric = metric.value
		if not self._use_aliases:
			raise ValueError("Aliases are not being used")
		return self._metric_to_alias[metric]
	
	def _serialize(self, p: spb.Payload) -> Union[bytes, spb.Payload]:
		"""Serializes the payload if auto_serialize is True, otherwise is a no-op."""
		if self.auto_serialize:
			if self.serialize_cast is not None:
				return self.serialize_cast(p.SerializeToString())
			return p.SerializeToString()
		return p
	
	def getNodeDeathPayload(self):
		"""Returns a death payload for the node. This must be requested and sent as part of the connection."""
		self.node_death_requested = True
		return self._serialize(spb.getNodeDeathPayload())

	def getNodeBirthPayload(self, state: MetricValues, times: MetricTimes = dict(), ignore_missing_node_death: bool = False):
		"""Returns a birth payload for the given state. State must be set for all metrics. Times can be set for specific metrics, if desired."""
		state = self._preprocess_dict(state)
		times = self._preprocess_dict(times, is_time=True)
		
		if not ignore_missing_node_death and not self.node_death_requested:
			raise ValueError("Must request death before requesting new birth")
		if set(COMMAND_METRICS | state.keys()) != set(self.all_metrics):
			raise ValueError("Node birth metrics must be the same as the model's metrics")

		payload = spb.getNodeBirthPayload()

		for metric in COMMAND_METRICS:
			if metric not in state:
				state[metric] = False

		for metric, value in state.items():
			mt = self.metric_types[metric]

			self.last_published[metric] = value

			if metric in times:
				spb.addMetric(payload, metric, self._metric_to_alias[metric], mt, value, metric[times])
			else:
				spb.addMetric(payload, metric, self._metric_to_alias[metric], mt, value)

		return self._serialize(payload)
	
	def getDataPayload(self, state: MetricValues, times: MetricTimes = dict()):
		"""Returns a data payload for the given state. Times can be set for specific metrics, if desired."""
		state = self._preprocess_dict(state)
		times = self._preprocess_dict(times, is_time=True)
		
		if not set(state.keys()).issubset(set(self.all_metrics)):
			raise ValueError("Node data metrics must be a subset of the model's metrics")

		payload = spb.getDdataPayload()

		for metric, value in state.items():
			if value != self.last_published.get(metric, ...):
				mt = self.metric_types[metric]
				self.last_published[metric] = value
			
				if metric in times:
					spb.addMetric(payload, metric, self._metric_to_alias[metric], mt, value, times[metric])
				else:
					spb.addMetric(payload, metric, self._metric_to_alias[metric], mt, value)

		return self._serialize(payload)

@dataclass(frozen=True)
class SpbTopic:
	group_id: str
	edge_node_id: str

	device_id: str | None = None

	namespace: str = "spBv1.0"

	@property
	def template_string(self):
		return f"{self.namespace}/{self.group_id}/%s/{self.edge_node_id}/{self.device_id}" \
			if self.device_id else \
			f"{self.namespace}/{self.group_id}/%s/{self.edge_node_id}"

	def construct(self, mtype: str):
		"""Constructs a Sparkplug B topic for the given message type. If a device_id is set, it will be included in the topic."""
		mtype = mtype.upper()
		return self.template_string % mtype

	@property
	def nbirth(self):
		return self.construct("NBIRTH")
	
	@property
	def NBIRTH(self):
		return self.construct("NBIRTH")
	
	@property
	def ndeath(self):
		return self.construct("NDEATH")
	
	@property
	def NDEATH(self):
		return self.construct("NDEATH")
	
	@property
	def dbirth(self):
		return self.construct("DBIRTH")
	
	@property
	def DBIRTH(self):
		return self.construct("DBIRTH")
	
	@property
	def ddeath(self):
		return self.construct("DDEATH")
	
	@property
	def DDEATH(self):
		return self.construct("DDEATH")
	
	@property
	def ndata(self):
		return self.construct("NDATA")
	
	@property
	def NDATA(self):
		return self.construct("NDATA")
	
	@property
	def ddata(self):
		return self.construct("DDATA")
	
	@property
	def ncmd(self):
		return self.construct("NCMD")
	
	@property
	def NCMD(self):
		return self.construct("NCMD")
	
	@property
	def dcmd(self):
		return self.construct("DCMD")
	
	@property
	def DCMD(self):
		return self.construct("DCMD")
	
	@property
	def state(self):
		return self.construct("STATE")
	
	@property
	def STATE(self):
		return self.construct("STATE")
	
	