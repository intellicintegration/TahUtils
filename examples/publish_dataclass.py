import time
from enum import Enum
from typing import Annotated
import paho.mqtt.client as mqtt
from tahutils import MetricDataType, SpbModel, SpbTopic
from tahutils import utils
from dataclasses import dataclass

@dataclass
class Fib:
	f1: MetricDataType.Int32
	f2: MetricDataType.Int32

@dataclass
class Metric:
	message: Annotated[MetricDataType.String, "Message"]
	steps: MetricDataType.Int32
	percent: MetricDataType.Float
	fib: Fib

def main():
	"""
	Publishes a birth message, then a series of data messages, and finally a death message.
	Assumes a local MQTT broker is running on the default port with no authentication.
	"""
	
	model = SpbModel(
		Metric,
		serialize_cast=bytes
	)
	topic = SpbTopic("testgroup", "testnode")
	
	mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "TahutilsPublishExample")
	
	mqttc.will_set(
		topic.ndeath,
		model.getDeathPayload(),
	)
	
	f1, f2 = 0, 1
	
	mqttc.connect("localhost", 1883)
	
	# Creating the dataclass instance for the birth payload
	data = Metric(
		message="Hello, world!",
		steps=0,
		percent=0.0,
		fib=Fib(f1=f1, f2=f2)
	)
	print(f"publish birth with data {data}")
	birth = model.getBirthPayload(data)
	mqttc.publish(
		topic.nbirth, 
		birth
	)
	
	n_steps = 5
	for i in range(1, n_steps+1):
		time.sleep(2)
		f1, f2 = f2, f1 + f2
		
		# Creating the dataclass instance for the data payload
		data.steps = i
		data.percent = i / n_steps
		data.fib.f1 = f1
		data.fib.f2 = f2
		
		if i == n_steps:
			data.message = "Goodbye, world!"
		
		print(f"publish {i} with data {data}")
		
		mqttc.publish(
			topic.ndata, 
			model.getDataPayload(data)
		)
		print(f"\tLast published state: {model.current_values}")
	
	# Remember, graceful disonnects don't prompt the will message!
	mqttc.publish(
		topic.ndeath,
		model.last_death
	)
	mqttc.disconnect()
	
	print(f"Last fib value: {model.get("fib/f2")}")

if __name__ == "__main__":
	main()
