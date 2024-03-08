# TahUtils

A small wrapper package for using [Tahu for Sparkplug B](https://github.com/eclipse/tahu) in Python. Comes with an unmodified (barring import structure) Tahu included, hence the use of the Eclipse license.

## Examples

See the `examples` directory in the project repository.

## Current Support

- Generating Sparkplug B topics
- Generating birth, death, and data payloads for nodes (not tested for devices)
- Managing aliases
- Using enums for metric names
- Parsing sparkplug b messages

## Updating Tahu Version

Assuming no major refactoring to the tahu library, updating the included tahu consists of the following steps:

1. Download the latest release from the repository: https://github.com/eclipse/tahu/tags
2. Extract the source code.
3. Regenerate the `sparkplug_b_pb2.py` file per the instructions in `tahu-<version>/python/core/README.md`. Use `tahu-<version>/python/core` as your working directory when executing the command, and you'll need the protobuf compiler.
4. Copy the contents of the `tahu-<version>/python/core` directory to the `tahutils/tahu` directory.
5. Overwrite the `tahutils/tahu/__init__.py` file with the appropriate imports, typically:

	```python
	from . import sparkplug_b_pb2
	from . import array_packer
	from . import sparkplug_b
	```

6. Modify the imports in `tahutils/tahu/sparkplug_b.py` to include the `tahu` package name:

	```python
	import tahutils.tahu.sparkplug_b_pb2 as sparkplug_b_pb2
	import time
	from tahutils.tahu.sparkplug_b_pb2 import Payload
	from tahutils.tahu.array_packer import *
	```
