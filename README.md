# TahUtils

A small wrapper package for using [Tahu for Sparkplug B](https://github.com/eclipse/tahu) in Python. Comes with an unmodified (barring import structure) Tahu included, hence the use of the Eclipse license.

## Examples

See the `examples` directory in the project repository.

## Current Support

- Generating Sparkplug B topics
- Generating birth, death, and data payloads for nodes and devices
- Managing aliases
- Using enums for metric names
- Using dataclasses to manage metric names and metric states
- Parsing sparkplug b messages

## Changes to the `tahu` library

### Updating compiled Protobuf files

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

### Fixing metric timestamps

As of this version, there is a bug in the `tahu` library relating to metric timestamps. See [this pull request](https://github.com/eclipse/tahu/pull/398) for more details.

This is patched by updating `sparkplug_b.py`.

```python
def addMetric(container, name, alias, type, value, timestamp=None):
    if timestamp is None:
        timestamp = int(round(time.time() * 1000))
	...

def addNullMetric(container, name, alias, type, timestamp=None):
    if timestamp is None:
        timestamp = int(round(time.time() * 1000))
    metric = container.metrics.add()
    if name is not None:
        metric.name = name
    if alias is not None:
        metric.alias = alias
    metric.timestamp = timestamp
    metric.is_null = True
	...
```