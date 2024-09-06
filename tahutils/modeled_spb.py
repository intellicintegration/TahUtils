from dataclasses import dataclass, is_dataclass, fields

_UNSET = object()

def fill_with_unset(cls):
	if not is_dataclass(cls):
		raise ValueError("The provided class is not a dataclass")
	
	# Initialize an empty dictionary to hold field values
	field_values = {}
	
	# Iterate over each field in the dataclass
	for field in fields(cls):
		field_type = field.type
		
		# Check if the field type is a dataclass itself
		if is_dataclass(field_type):
			field_values[field.name] = fill_with_unset(field_type)
		else:
			field_values[field.name] = _UNSET
	
	# Create a new instance of the dataclass with ellipsis in all fields
	return cls(**field_values)

class ObjectDrivenSPBModel:
	def __init__(self, model_class):
		if not is_dataclass(model_class):
			raise ValueError("model_class must be a dataclass")
		self._model = fill_with_unset(model_class)

	@property
	def model(self):
		return self._model