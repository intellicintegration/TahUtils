import time
from enum import Enum

import paho.mqtt.client as mqtt

from tahutils import SpbModel, SpbTopic, MetricDataType

class Metric(Enum):
	message = "message"
	steps = "steps"
	percent = "percent"

def main():
	model = SpbModel(
		{
			Metric.message: MetricDataType.String,
			Metric.steps: MetricDataType.Int32,
			Metric.percent: MetricDataType.Float,
		}
	)
	topic = SpbTopic("testgroup", "testnode")

	
	mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "spb_tester")
	mqttc.will_set(
		topic.ndeath,
		model.getNodeDeathPayload(),
	)
	mqttc.connect("localhost", 1883)
	data = {
			Metric.message: "Hello, world!",
			Metric.steps: 0,
			Metric.percent: 0,
		}
	print(f"publish birth with data {data}")
	birth = model.getNodeBirthPayload(data)
	mqttc.publish(
		topic.nbirth, 
		bytes(birth)
	)

	n_steps = 5
	for i in range(1, n_steps+1):
		time.sleep(2)
		data = {
			Metric.steps: i,
			Metric.percent: i / n_steps,
		}
		if i == n_steps:
			data[Metric.message] = "Goodbye, world!"
		
		print(f"publish {i} with data {data}")

		mqttc.publish(
			topic.ndata, 
			model.getDataPayload(data)
		)
	mqttc.disconnect()

if __name__ == "__main__":
	main()