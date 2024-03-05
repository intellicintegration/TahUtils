from tahutils.tahu import sparkplug_b as spb
from typing import Any, Union

COMMAND_METRICS = ["Node Control/Next Server", "Node Control/Rebirth", "Node Control/Reboot"]

class SpbModel:
	def __init__(self, metrics: dict[str, spb.MetricDataType], use_aliases: bool=False, auto_serialize: bool=True) -> None:
		self.metrics = list(metrics.keys())
		self.metric_types = {k:v for k,v in metrics.items()}

		self.last_published = {}

		self._use_aliases = use_aliases
		all_metrics = COMMAND_METRICS + self.metrics
		self.alias = {metric: i for i, metric in enumerate(all_metrics)} \
			if self._use_aliases else \
			{metric: None for metric in all_metrics}
		
		if self._use_aliases:
			self._alias_to_metric = {i: metric for i, metric in self.alias.items()}

		self.auto_serialize = auto_serialize

		self.node_death_requested = False

	@property
	def aliasing(self) -> bool:
		return self._use_aliases
	
	def _serialize(self, p: spb.Payload) -> Union[bytearray, spb.Payload]:
		if self.auto_serialize:
			return bytearray(p.SerializeToString())
		return p
	
	def getNodeDeathPayload(self):
		self.node_death_requested = True
		return self._serialize(spb.getNodeDeathPayload())

	def getNodeBirthPayload(self, state: dict[str, Any], times = dict()):
		if not self.node_death_requested:
			raise ValueError("Must request death before requesting new birth")
		if set(state.keys()) != set(self.metrics):
			raise ValueError("Node birth metrics must be the same as the model's metrics")

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
	
	def getDataPayload(self, state: dict[str, Any], times = dict()):
		if not set(state.keys()).issubset(set(self.metrics)):
			raise ValueError("Node data metrics must be a subset of the model's metrics")
		
		payload = spb.getDdataPayload()
		
		for metric, value in state.items():
			if value != self.last_published.get(metric, ...):
				mt = self.metric_types[metric]
				self.last_published[metric] = value
			
				if metric in times:
					spb.addMetric(payload, metric, self.alias[metric], mt, value, metric[times])
				else:
					spb.addMetric(payload, metric, self.alias[metric], mt, value)

		return self._serialize(payload)
