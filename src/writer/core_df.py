"""
`core_df` contains classes and functions that allow you to manipulate editable dataframes.
"""
import copy
from abc import ABCMeta
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type, Union

import pyarrow  # type: ignore

from .core import MutableValue, import_failure
from .ss_types import DataFrameRecordAdded, DataFrameRecordRemoved, DataFrameRecordUpdated

if TYPE_CHECKING:
    import pandas
    import polars


class DataframeRecordProcessor():
    """
    This interface defines the signature of the methods to process the events of a
    dataframe compatible with EditableDataframe.

    A Dataframe can be any structure composed of tabular data.

    This class defines the signature of the methods to be implemented.
    """
    __metaclass__ = ABCMeta

    @staticmethod
    def match(df: Any) -> bool:
        """
        This method checks if the dataframe is compatible with the processor.
        """
        raise NotImplementedError

    @staticmethod
    def record(df: Any, record_index: int) -> dict:
        """
        This method read a record at the given line and get it back as dictionary

        >>> edf = EditableDataFrame(df)
        >>> r = edf.record(1)
        """
        raise NotImplementedError

    @staticmethod
    def record_add(df: Any, payload: DataFrameRecordAdded) -> Any:
        """
        signature of the methods to be implemented to process wf-dataframe-add event

        >>> edf = EditableDataFrame(df)
        >>> edf.record_add({"record": {"a": 1, "b": 2}})
        """
        raise NotImplementedError

    @staticmethod
    def record_update(df: Any, payload: DataFrameRecordUpdated) -> Any:
        """
        signature of the methods to be implemented to process wf-dataframe-update event

        >>> edf = EditableDataFrame(df)
        >>> edf.record_update({"record_index": 12, "record": {"a": 1, "b": 2}})
        """
        raise NotImplementedError

    @staticmethod
    def record_remove(df: Any, payload: DataFrameRecordRemoved) -> Any:
        """
        signature of the methods to be implemented to process wf-dataframe-action event

        >>> edf = EditableDataFrame(df)
        >>> edf.record_remove({"record_index": 12})
        """
        raise NotImplementedError

    @staticmethod
    def pyarrow_table(df: Any) -> pyarrow.Table:
        """
        Serializes the dataframe into a pyarrow table
        """
        raise NotImplementedError


class PandasRecordProcessor(DataframeRecordProcessor):
    """
    PandasRecordProcessor processes records from a pandas dataframe saved into an EditableDataframe

    >>> df = pandas.DataFrame({"a": [1, 2], "b": [3, 4]})
    >>> edf = EditableDataFrame(df)
    >>> edf.record_add({"a": 1, "b": 2})
    """

    @staticmethod
    @import_failure(rvalue=False)
    def match(df: Any) -> bool:
        import pandas
        return True if isinstance(df, pandas.DataFrame) else False

    @staticmethod
    def record(df: 'pandas.DataFrame', record_index: int) -> dict:
        """

        >>> edf = EditableDataFrame(df)
        >>> r = edf.record(1)
        """
        import pandas

        record = df.iloc[record_index]
        if not isinstance(df.index, pandas.RangeIndex):
            index_list = df.index.tolist()
            record_index_content = index_list[record_index]
            if isinstance(record_index_content, tuple):
                for i, n in enumerate(df.index.names):
                    record[n] = record_index_content[i]
            else:
                record[df.index.names[0]] = record_index_content

        return dict(record)

    @staticmethod
    def record_add(df: 'pandas.DataFrame', payload: DataFrameRecordAdded) -> 'pandas.DataFrame':
        """
        >>> edf = EditableDataFrame(df)
        >>> edf.record_add({"record": {"a": 1, "b": 2}})
        """
        import pandas

        _assert_record_match_pandas_df(df, payload['record'])

        record, index = _split_record_as_pandas_record_and_index(payload['record'], df.index.names)

        if isinstance(df.index, pandas.RangeIndex):
            new_df = pandas.DataFrame([record])
            return pandas.concat([df, new_df], ignore_index=True)
        else:
            new_df = pandas.DataFrame([record], index=[index])
            return pandas.concat([df, new_df])

    @staticmethod
    def record_update(df: 'pandas.DataFrame', payload: DataFrameRecordUpdated) -> 'pandas.DataFrame':
        """
        >>> edf = EditableDataFrame(df)
        >>> edf.record_update({"record_index": 12, "record": {"a": 1, "b": 2}})
        """
        import pandas

        _assert_record_match_pandas_df(df, payload['record'])

        record: dict
        record, index = _split_record_as_pandas_record_and_index(payload['record'], df.index.names)

        record_index = payload['record_index']

        if isinstance(df.index, pandas.RangeIndex):
            df.iloc[record_index] = record  # type: ignore
        else:
            df.iloc[record_index] = record  # type: ignore
            index_list = df.index.tolist()
            index_list[record_index] = index
            df.index = index_list  # type: ignore

        return df

    @staticmethod
    def record_remove(df: 'pandas.DataFrame', payload: DataFrameRecordRemoved) -> 'pandas.DataFrame':
        """
        >>> edf = EditableDataFrame(df)
        >>> edf.record_remove({"record_index": 12})
        """
        record_index: int = payload['record_index']
        idx = df.index[record_index]
        df = df.drop(idx)

        return df

    @staticmethod
    def pyarrow_table(df: 'pandas.DataFrame') -> pyarrow.Table:
        """
        Serializes the dataframe into a pyarrow table
        """
        table = pyarrow.Table.from_pandas(df=df)
        return table


class PolarRecordProcessor(DataframeRecordProcessor):
    """
    PolarRecordProcessor processes records from a polar dataframe saved into an EditableDataframe

    >>> df = polars.DataFrame({"a": [1, 2], "b": [3, 4]})
    >>> edf = EditableDataFrame(df)
    >>> edf.record_add({"record": {"a": 1, "b": 2}})
    """

    @staticmethod
    @import_failure(rvalue=False)
    def match(df: Any) -> bool:
        import polars
        return True if isinstance(df, polars.DataFrame) else False

    @staticmethod
    def record(df: 'polars.DataFrame', record_index: int) -> dict:
        """

        >>> edf = EditableDataFrame(df)
        >>> r = edf.record(1)
        """
        record = {}
        r = df[record_index]
        for c in r.columns:
            record[c] = df[record_index, c]

        return record


    @staticmethod
    def record_add(df: 'polars.DataFrame', payload: DataFrameRecordAdded) -> 'polars.DataFrame':
        _assert_record_match_polar_df(df, payload['record'])

        import polars
        new_df = polars.DataFrame([payload['record']])
        return polars.concat([df, new_df])

    @staticmethod
    def record_update(df: 'polars.DataFrame', payload: DataFrameRecordUpdated) -> 'polars.DataFrame':
        # This implementation works but is not optimal.
        # I didn't find a better way to update a record in polars
        #
        # https://github.com/pola-rs/polars/issues/5973
        _assert_record_match_polar_df(df, payload['record'])

        record = payload['record']
        record_index = payload['record_index']
        for r in record:
            df[record_index, r] = record[r]

        return df

    @staticmethod
    def record_remove(df: 'polars.DataFrame', payload: DataFrameRecordRemoved) -> 'polars.DataFrame':
        import polars

        record_index: int = payload['record_index']
        df_filtered = polars.concat([df[:record_index], df[record_index + 1:]])
        return df_filtered

    @staticmethod
    def pyarrow_table(df: 'polars.DataFrame') -> pyarrow.Table:
        """
        Serializes the dataframe into a pyarrow table
        """
        import pyarrow.interchange  # type: ignore
        table: pyarrow.Table = pyarrow.interchange.from_dataframe(df)
        return table

class RecordListRecordProcessor(DataframeRecordProcessor):
    """
    RecordListRecordProcessor processes records from a list of record saved into an EditableDataframe

    >>> df = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    >>> edf = EditableDataFrame(df)
    >>> edf.record_add({"record": {"a": 1, "b": 2}})
    """

    @staticmethod
    def match(df: Any) -> bool:
        return True if isinstance(df, list) else False


    @staticmethod
    def record(df: List[Dict[str, Any]], record_index: int) -> dict:
        """

        >>> edf = EditableDataFrame(df)
        >>> r = edf.record(1)
        """
        r = df[record_index]
        return copy.copy(r)

    @staticmethod
    def record_add(df: List[Dict[str, Any]], payload: DataFrameRecordAdded) -> List[Dict[str, Any]]:
        _assert_record_match_list_of_records(df, payload['record'])
        df.append(payload['record'])
        return df

    @staticmethod
    def record_update(df: List[Dict[str, Any]], payload: DataFrameRecordUpdated) -> List[Dict[str, Any]]:
        _assert_record_match_list_of_records(df, payload['record'])

        record_index = payload['record_index']
        record = payload['record']

        df[record_index] = record
        return df

    @staticmethod
    def record_remove(df: List[Dict[str, Any]], payload: DataFrameRecordRemoved) -> List[Dict[str, Any]]:
        del(df[payload['record_index']])
        return df

    @staticmethod
    def pyarrow_table(df: List[Dict[str, Any]]) -> pyarrow.Table:
        """
        Serializes the dataframe into a pyarrow table
        """
        column_names = list(df[0].keys())
        columns = {key: [record[key] for record in df] for key in column_names}

        pyarrow_columns = {key: pyarrow.array(values) for key, values in columns.items()}
        schema = pyarrow.schema([(key, pyarrow_columns[key].type) for key in pyarrow_columns])
        table = pyarrow.Table.from_arrays(
            [pyarrow_columns[key] for key in column_names],
            schema=schema
        )

        return table

class EditableDataFrame(MutableValue):
    """
    Editable Dataframe makes it easier to process events from components
    that modify a dataframe like the dataframe editor.

    >>> initial_state = wf.init_state({
    >>>    "df": wf.EditableDataFrame(df)
    >>> })

    Editable Dataframe is compatible with a pandas, thrillers or record list dataframe
    """
    processors = [PandasRecordProcessor, PolarRecordProcessor, RecordListRecordProcessor]

    def __init__(self, df: Union['pandas.DataFrame', 'polars.DataFrame', List[dict]]):
        super().__init__()
        self._df = df
        self.processor: Type[DataframeRecordProcessor]
        for processor in self.processors:
            if processor.match(self.df):
                self.processor = processor
                break

        if self.processor is None:
            raise ValueError("The dataframe must be a pandas, polar Dataframe or a list of record")

    @property
    def df(self) -> Union['pandas.DataFrame', 'polars.DataFrame', List[dict]]:
        return self._df

    @df.setter
    def df(self, value: Union['pandas.DataFrame', 'polars.DataFrame', List[dict]]) -> None:
        self._df = value
        self.mutate()

    def record_add(self, payload: DataFrameRecordAdded) -> None:
        """
        Adds a record to the dataframe

        >>> df = pandas.DataFrame({"a": [1, 2], "b": [3, 4]})
        >>> edf = EditableDataFrame(df)
        >>> edf.record_add({"record": {"a": 1, "b": 2}})
        """
        assert self.processor is not None

        self._df = self.processor.record_add(self.df, payload)
        self.mutate()

    def record_update(self, payload: DataFrameRecordUpdated) -> None:
        """
        Updates a record in the dataframe

        The record must be complete otherwise an error is raised (ValueError).
        It must a value for each index / column.

        >>> df = pandas.DataFrame({"a": [1, 2], "b": [3, 4]})
        >>> edf = EditableDataFrame(df)
        >>> edf.record_update({"record_index": 0, "record": {"a": 2, "b": 2}})
        """
        assert self.processor is not None

        self._df = self.processor.record_update(self.df, payload)
        self.mutate()

    def record_remove(self, payload: DataFrameRecordRemoved) -> None:
        """
        Removes a record from the dataframe

        >>> df = pandas.DataFrame({"a": [1, 2], "b": [3, 4]})
        >>> edf = EditableDataFrame(df)
        >>> edf.record_remove({"record_index": 0})
        """
        assert self.processor is not None

        self._df = self.processor.record_remove(self.df, payload)
        self.mutate()

    def pyarrow_table(self) -> pyarrow.Table:
        """
        Serializes the dataframe into a pyarrow table

        This mechanism is used for serializing data for transmission to the frontend.

        >>> df = pandas.DataFrame({"a": [1, 2], "b": [3, 4]})
        >>> edf = EditableDataFrame(df)
        >>> pa_table = edf.pyarrow_table()
        """
        assert self.processor is not None

        pa_table = self.processor.pyarrow_table(self.df)
        return pa_table

    def record(self, record_index: int):
        """
        Retrieves a specific record in dictionary form.

        :param record_index:
        :return:
        """
        assert self.processor is not None

        record = self.processor.record(self.df, record_index)
        return record



def _assert_record_match_pandas_df(df: 'pandas.DataFrame', record: Dict[str, Any]) -> None:
    """
    Asserts that the record matches the dataframe columns & index

    >>> _assert_record_match_pandas_df(pandas.DataFrame({"a": [1, 2], "b": [3, 4]}), {"a": 1, "b": 2})
    """
    import pandas

    columns = set(list(df.columns.values) + df.index.names) if isinstance(df.index, pandas.RangeIndex) is False else set(df.columns.values)
    columns_record = set(record.keys())
    if columns != columns_record:
        raise ValueError(f"Columns mismatch. Expected {columns}, got {columns_record}")

def _assert_record_match_polar_df(df: 'polars.DataFrame', record: Dict[str, Any]) -> None:
    """
    Asserts that the record matches the columns of polar dataframe

    >>> _assert_record_match_pandas_df(polars.DataFrame({"a": [1, 2], "b": [3, 4]}), {"a": 1, "b": 2})
    """
    columns = set(df.columns)
    columns_record = set(record.keys())
    if columns != columns_record:
        raise ValueError(f"Columns mismatch. Expected {columns}, got {columns_record}")

def _assert_record_match_list_of_records(df: List[Dict[str, Any]], record: Dict[str, Any]) -> None:
    """
    Asserts that the record matches the key in the record list (it use the first record to check)

    >>> _assert_record_match_list_of_records([{"a": 1, "b": 2}, {"a": 3, "b": 4}], {"a": 1, "b": 2})
    """
    if len(df) == 0:
        return

    columns = set(df[0].keys())
    columns_record = set(record.keys())
    if columns != columns_record:
        raise ValueError(f"Columns mismatch. Expected {columns}, got {columns_record}")



def _split_record_as_pandas_record_and_index(param: dict, index_columns: list) -> Tuple[dict, tuple]:
    """
    Separates a record into the record part and the index part to be able to
    create or update a row in a dataframe.

    >>> record, index = _split_record_as_pandas_record_and_index({"a": 1, "b": 2}, ["a"])
    >>> print(record) # {"b": 2}
    >>> print(index) # (1,)
    """
    final_record = {}
    final_index = []
    for key, value in param.items():
        if key in index_columns:
            final_index.append(value)
        else:
            final_record[key] = value

    return final_record, tuple(final_index)
