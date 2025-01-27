"""
Serializes values before sending them to the front end.
Provides JSON-compatible values, including data URLs for binary data.
"""

import datetime
import inspect
import io
import math
from typing import Any, Dict, List, Union

import writer.core


def serialize(v: Any) -> Union[Dict, List, str, bool, int, float, None]:
    from writer.ai import Conversation
    from writer.core_df import EditableDataFrame

    if isinstance(v, writer.core.WriterState):
        return _serialize_dict_recursively(v._state_data)
    if isinstance(v, Conversation):
        return v.serialized_messages
    if isinstance(v, (writer.core.FileWrapper, writer.core.BytesWrapper)):
        return _serialize_ss_wrapper(v)
    if isinstance(v, (datetime.datetime, datetime.date)):
        return str(v)
    if isinstance(v, bytes):
        return serialize(writer.core.BytesWrapper(v))
    if isinstance(v, dict):
        return _serialize_dict_recursively(v)
    if isinstance(v, list):
        return _serialize_list_recursively(v)
    if isinstance(v, (str, bool)):
        return v
    if isinstance(v, EditableDataFrame):
        table = v.pyarrow_table()
        return _serialize_pyarrow_table(table)
    if v is None:
        return v

    # Checking the MRO allows to determine object type without creating dependencies
    # to these packages

    v_mro = [
        f"{x.__module__}.{x.__name__}" for x in inspect.getmro(type(v))]

    if isinstance(v, (int, float)):
        if "numpy.float64" in v_mro:
            return float(v)
        if math.isnan(v):
            return None
        return v

    if "pandas.core.frame.DataFrame" in v_mro:
        return _serialize_pandas_dataframe(v)
    if hasattr(v, "__dataframe__"):
        return _serialize_dataframe(v)

    if "matplotlib.figure.Figure" in v_mro:
        return _serialize_matplotlib_fig(v)
    if "plotly.graph_objs._figure.Figure" in v_mro:
        return v.to_json()
    if "numpy.float64" in v_mro:
        return float(v)
    if "numpy.ndarray" in v_mro:
        return _serialize_list_recursively(v.tolist())
    if "pyarrow.lib.Table" in v_mro:
        return _serialize_pyarrow_table(v)

    if hasattr(v, "to_dict") and callable(v.to_dict):
        # Covers Altair charts, Plotly graphs
        return _serialize_dict_recursively(v.to_dict())

    return(f"Object of type { type(v) } (MRO: {v_mro}) cannot be serialized.")

def _serialize_dict_recursively(d: Dict) -> Dict:
    return {str(k): serialize(v) for k, v in d.items()}

def _serialize_list_recursively(l: List) -> List:  # noqa: E741
    return [serialize(v) for v in l]

def _serialize_ss_wrapper(v: Union["writer.core.FileWrapper", "writer.core.BytesWrapper"]) -> str:
    return v.get_as_dataurl()

def _serialize_matplotlib_fig(fig) -> str:
    # It's safe to import matplotlib here without listing it as a dependency.
    # If this method is called, it's because a matplotlib figure existed.
    # Note: matplotlib type needs to be ignored since it doesn't provide types
    import matplotlib.pyplot as plt  # type: ignore

    iobytes = io.BytesIO()
    fig.savefig(iobytes, format="png")
    iobytes.seek(0)
    plt.close(fig)
    return writer.core.FileWrapper(iobytes, "image/png").get_as_dataurl()

def _serialize_dataframe(df) -> str:
    """
    Serialize a dataframe with pyarrow a dataframe that implements
    the Dataframe Interchange Protocol i.e. the __dataframe__() method

    :param df: dataframe that implements Dataframe Interchange Protocol (__dataframe__ method)
    :return: a arrow file as a dataurl (application/vnd.apache.arrow.file)
    """
    import pyarrow.interchange  # type: ignore
    table = pyarrow.interchange.from_dataframe(df)
    return _serialize_pyarrow_table(table)

def _serialize_pandas_dataframe(df):
    import pyarrow as pa  # type: ignore
    pa_table = pa.Table.from_pandas(df, preserve_index=True)
    return _serialize_pyarrow_table(pa_table)

def _serialize_pyarrow_table(table):
    import pyarrow as pa  # type: ignore

    sink = pa.BufferOutputStream()
    batches = table.to_batches()
    with pa.ipc.new_file(sink, table.schema) as writer:
        for batch in batches:
            writer.write_batch(batch)
    buf = sink.getvalue()
    bw = writer.core.BytesWrapper(buf, "application/vnd.apache.arrow.file")
    return serialize(bw)

class WriterSerializerException(ValueError):
    pass