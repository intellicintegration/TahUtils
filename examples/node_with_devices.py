import time
from enum import Enum
from typing import Annotated
import paho.mqtt.client as mqtt
from tahutils import MetricDataType, DictSpbNode, SpbTopic
from tahutils import utils
from dataclasses import dataclass

@dataclass
class DeviceData:
	constantnum: Annotated[MetricDataType.Int32, "Constant Number"]
	count: Annotated[MetricDataType.Int32, "Counter"]

@dataclass
class NodeData:
	message: Annotated[MetricDataType.String, "Message"]
	steps: Annotated[MetricDataType.Int32, "Steps"]

def main():
	"""
	Publishes a birth message, then a series of data messages, and finally a death message.
	Assumes a local MQTT broker is running on the default port with no authentication.
	"""

	n_devices = 2

	node_model = DictSpbNode(
		NodeData,
		serialize_cast=bytes
	)
	device_models = [
		DictSpbNode(
			DeviceData,
			serialize_cast=bytes,
			is_device=True
		) for _ in range(n_devices)
	]
	node_topic = SpbTopic("testgroup", "TestNodeWithDevices")
	device_topics = [
		node_topic.construct_device_topic(f"Device{i}") for i in range(n_devices)
	]
	
	mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "TahutilsPublishExample")
	
	mqttc.will_set(
		node_topic.ndeath,
		node_model.getDeathPayload(),
	)
	
	mqttc.connect("localhost", 1883)
	
	# Creating the dataclass instance for the birth payload
	node_data = NodeData(
		message="Hello, world!",
		steps=0
	)
	device_datas = [
		DeviceData(
			constantnum=i,
			count=0
		) for i in range(n_devices)
	]
	birth = node_model.getBirthPayload(node_data)
	mqttc.publish(
		node_topic.nbirth, 
		birth
	)
	for i in range(n_devices):
		mqttc.publish(
			device_topics[i].dbirth,
			device_models[i].getBirthPayload(device_datas[i])
		)	
	
	n_steps = 5
	for i in range(1, n_steps+1):
		print(f"Publishing data message {i}")
		time.sleep(2)

		for i in range(n_devices):
			device_datas[i].count += 1
			mqttc.publish(
				device_topics[i].ddata,
				device_models[i].getDataPayload(device_datas[i])
			)
	
	print("Publishing death messages...")
	# The node death kills all devices
	mqttc.publish(
		node_topic.ndeath,
		node_model.last_death
	)
	mqttc.disconnect()


if __name__ == "__main__":
	main()
