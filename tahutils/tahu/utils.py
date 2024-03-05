from dataclasses import dataclass
from tahu import sparkplug_b as spb
from typing import Any

@dataclass
class ParsedMetric:
    name: str
    value: Any
    timestamp: float
    datatype: int

    @property
    def is_null(self):
        return self.value is None

def parse_dataset_value(m, dtype: int):
    dsdt = spb.DataSetDataType

    val = None
    if dsdt.Int8 <= dtype <= dsdt.Int32 or dsdt.UInt8 <= dtype <= dsdt.UInt32:
        val = m.int_value
    elif dtype in [dsdt.Int64, dsdt.UInt64]:
        val = m.long_value
    elif dtype == dsdt.Float:
        val = m.float_value
    elif dtype == dsdt.Double:
        val = m.double_value
    elif dtype == dsdt.Boolean:
        val = m.boolean_value
    elif dtype == dsdt.String:
        val = m.string_value
    elif dtype == dsdt.DateTime:
        val = m.long_value
    else:
        raise NotImplementedError("Unhandled dataset data type %d", dtype)
    return val


def parse_metric_value(m):
    mdt = spb.MetricDataType

    val = None
    dtype = m.datatype 
    if m.is_null:
        val = None
    elif mdt.Int8 <= dtype <= mdt.Int32 or mdt.UInt8 <= dtype <= mdt.UInt32:
        val = m.int_value
    elif dtype in [mdt.Int64, mdt.UInt64]:
        val = m.long_value
    elif dtype == mdt.Float:
        val = m.float_value
    elif dtype == mdt.Double:
        val = m.double_value
    elif dtype == mdt.Boolean:
        val = m.boolean_value
    elif dtype == mdt.String:
        val = m.string_value
    elif dtype == mdt.DateTime:
        val = m.long_value
    elif dtype == mdt.DataSet:
        d = m.dataset_value
        val = [
            [
                parse_dataset_value(element, t) 
                for element, t in zip(row.elements, d.types)
            ]
            for row in d.rows
        ]
    else:
        raise NotImplementedError("Unhandled metric data type %d", dtype)
    return val