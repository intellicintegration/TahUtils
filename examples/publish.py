import time
from enum import Enum

import paho.mqtt.client as mqtt

from tahutils import MetricDataType, SpbModel, SpbTopic

"""
Enums can be used to define the metric names. This is useful for ensuring that the metric names are consistent across the application.
"""
class Metric(Enum):
	message = "message"
	steps = "steps"
	percent = "percent"
	fib = "fib"

class Fib(Enum):
	f1 = "f1"
	f2 = "f2"

def main():
	"""
	Publishes a birth message, then a series of data messages, and finally a death message.
	Assumes a local MQTT broker is running on the default port with no authentication.
	"""


	"""
	When constructing the SpbModel, every metric must be defined with its corresponding MetricDataType.
	Additionally, we set the serialize_cast to the datatype expected by the MQTT client's publish method.
	"""
	model = SpbModel(
		{
			Metric.message: MetricDataType.String,
			Metric.steps: MetricDataType.Int32,
			Metric.percent: MetricDataType.Float,
			Metric.fib: {
				Fib.f1: MetricDataType.Int32,
				Fib.f2: MetricDataType.Int32,
			}
		},
		serialize_cast=bytes
	)
	topic = SpbTopic("testgroup", "testnode")

	mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "TahutilsPublishExample")

	"""
	We must get the death payload before connecting to the broker. This is because the will payload is sent as part of the connection process.
	Additionally, the death payload must be generated before a birth payload is requested. 
	"""
	mqttc.will_set(
		topic.ndeath,
		model.getNodeDeathPayload(),
	)
	
	f1, f2 = 0, 1

	mqttc.connect("localhost", 1883)
	data = {
		Metric.message: "Hello, world!",
		Metric.steps: 0,
		Metric.percent: 0,
		Metric.fib: {
			Fib.f1: f1,
			Fib.f2: f2,
		}
	}
	print(f"publish birth with data {data}")
	birth = model.getNodeBirthPayload(data)
	mqttc.publish(
		topic.nbirth, 
		birth
	)

	n_steps = 5
	for i in range(1, n_steps+1):
		time.sleep(2)
		f1, f2 = f2, f1 + f2


		"""
		Data for NDATA/DDATA doesn't have to be a complete set of metrics.
		"""
		data = {
			Metric.steps: i,
			Metric.percent: i / n_steps,
			Metric.fib: {
				Fib.f1: f1,
				Fib.f2: f2,
			}
		}
		if i == n_steps:
			data[Metric.message] = "Goodbye, world!"
		
		print(f"publish {i} with data {data}")

		mqttc.publish(
			topic.ndata, 
			model.getDataPayload(data)
		)
		print(f"\tLast published state: {model.current_values}")
	mqttc.disconnect()

	print(f"Last fib value: {model.get(Metric.fib, Fib.f2)}")

if __name__ == "__main__":
	main()