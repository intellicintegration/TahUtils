from dataclasses import dataclass
from typing import Optional
from functools import cached_property

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
	
	@cached_property
	def is_device(self):
		return self.device_id is not None

	def construct(self, mtype: str) -> str:
		"""Constructs a Sparkplug B topic for the given message type. If a device_id is set, it will be included in the topic."""
		mtype = mtype.upper()
		return self.template_string % mtype
	
	def construct_device_topic(self, device_id: Optional[str]):
		"""Constructs and returns an SpbTopic from this one with the given device_id. Can pass `None` to remove the device_id."""
		return SpbTopic(
			group_id=self.group_id,
			edge_node_id=self.edge_node_id,
			device_id=device_id,
			namespace=self.namespace
		)

	@cached_property
	def nbirth(self):
		return self.construct("NBIRTH")
	
	@cached_property
	def NBIRTH(self):
		return self.construct("NBIRTH")
	
	@cached_property
	def ndeath(self):
		return self.construct("NDEATH")
	
	@cached_property
	def NDEATH(self):
		return self.construct("NDEATH")
	
	@cached_property
	def dbirth(self):
		return self.construct("DBIRTH")
	
	@cached_property
	def DBIRTH(self):
		return self.construct("DBIRTH")
	
	@cached_property
	def ddeath(self):
		return self.construct("DDEATH")
	
	@cached_property
	def DDEATH(self):
		return self.construct("DDEATH")
	
	@cached_property
	def ndata(self):
		return self.construct("NDATA")
	
	@cached_property
	def NDATA(self):
		return self.construct("NDATA")
	
	@cached_property
	def ddata(self):
		return self.construct("DDATA")
	
	@cached_property
	def ncmd(self):
		return self.construct("NCMD")
	
	@cached_property
	def NCMD(self):
		return self.construct("NCMD")
	
	@cached_property
	def dcmd(self):
		return self.construct("DCMD")
	
	@cached_property
	def DCMD(self):
		return self.construct("DCMD")
	
	@cached_property
	def state(self):
		return self.construct("STATE")
	
	@cached_property
	def STATE(self):
		return self.construct("STATE")
	
	