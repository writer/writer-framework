from pathlib import Path
from typing import Dict

import pytest
from tests.backend import parse_instance_path
import writer as wf
from writer import audit_and_fix, wf_project
from writer.core import (
    EventDeserializer,
    SessionManager,
    import_failure,
)
from writer.ss_types import WriterEvent
import pandas
import polars

wf.Config.is_mail_enabled_for_log = True

_, sc = wf_project.read_files(Path(__file__).resolve().parent / "basic_test_app")
sc = audit_and_fix.fix_components(sc)

session = wf.session_manager.get_new_session()
session.session_component_tree.ingest(sc)

class TestEventDeserializer:

    ed = EventDeserializer(session)

    def test_unknown_no_payload(self) -> None:
        ev = WriterEvent(
            type="not-a-known-event",
            instancePath=parse_instance_path("root:0"),
            payload=None
        )
        self.ed.transform(ev)
        assert ev.type == "not-a-known-event"

    def test_unknown_with_payload(self) -> None:
        ev = WriterEvent(
            type="not-a-known-event",
            instancePath=parse_instance_path("root:0"),
            payload={"has_payload": "yes"}
        )
        assert ev.type == "not-a-known-event"

    def test_unknown_native_with_payload(self) -> None:
        ev = WriterEvent(
            type="wf-not-a-known-event",
            instancePath=parse_instance_path("root:0"),
            payload={"has_payload": "yes"}
        )
        assert ev.type == "wf-not-a-known-event"
        with pytest.raises(ValueError):
            self.ed.transform(ev)

    def test_number_change(self) -> None:
        ev = WriterEvent(
            type="wf-number-change",
            instancePath=parse_instance_path("root:0"),
            payload="44"
        )
        self.ed.transform(ev)
        assert ev.payload == 44

    def test_change(self) -> None:
        ev = WriterEvent(
            type="wf-change",
            instancePath=parse_instance_path("root:0"),
            payload="44 !@"
        )
        self.ed.transform(ev)
        assert ev.payload == "44 !@"

    def test_option_change_default(self) -> None:
        ev_valid = WriterEvent(
            type="wf-option-change",
            instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,wzudartz9sn1785b:0"),
            payload="a"
        )

        self.ed.transform(ev_valid)
        assert ev_valid.payload == "a"

        ev_invalid = WriterEvent(
            type="wf-option-change",
            instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,wzudartz9sn1785b:0"),
            payload="d"
        )

        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

    def test_option_change(self) -> None:
        ev_valid = WriterEvent(
            type="wf-option-change",
            instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,x3sy1kw7mybbklam:0"),
            payload="sp"
        )

        self.ed.transform(ev_valid)
        assert ev_valid.payload == "sp"

        ev_invalid = WriterEvent(
            type="wf-option-change",
            instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,x3sy1kw7mybbklam:0"),
            payload="se"
        )

        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

    def test_options_change_default(self) -> None:
        ev_valid = WriterEvent(
            type="wf-options-change",
            instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,aoyhvw30c0ncxg60:0"),
            payload=["a", "b"]
        )

        self.ed.transform(ev_valid)
        assert ev_valid.payload == ["a", "b"]

        ev_invalid = WriterEvent(
            type="wf-options-change",
            instancePath=parse_instance_path("root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,aoyhvw30c0ncxg60:0"),
            payload=["a", "d"]
        )

        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

    def test_hashchange(self) -> None:
        ev = WriterEvent(
            type="wf-hashchange",
            instancePath=parse_instance_path("root:0"),
            payload={
                "pageKey": "myPage",
                "routeVars": {
                    "param": "1"
                },
                "virus": "yes"
            }
        )
        self.ed.transform(ev)
        assert ev.payload == {
            "page_key": "myPage",
            "route_vars": {
                "param": "1"
            },
        }

    def test_webcam(self) -> None:
        ev = WriterEvent(
            type="wf-webcam",
            instancePath=parse_instance_path("root:0"),
            payload="data:text/plain;base64,aGVsbG8gd29ybGQ="
        )
        self.ed.transform(ev)
        assert bytes(ev.payload).decode("utf-8") == "hello world"

    def test_file_change(self) -> None:
        ev = WriterEvent(
            type="wf-file-change",
            instancePath=parse_instance_path("root:0"),
            payload=[{
                "name": "myfile.txt",
                "type": "text/plain",
                "data": "data:text/plain;base64,aGVsbG8gd29ybGQ="
            }]
        )
        self.ed.transform(ev)
        assert ev.payload[0].get("name") == "myfile.txt"
        assert ev.payload[0].get("type") == "text/plain"
        assert bytes(ev.payload[0].get("data")).decode(
            "utf-8") == "hello world"

    def test_date_change(self) -> None:
        ev_invalid = WriterEvent(
            type="wf-date-change",
            instancePath=parse_instance_path("root:0"),
            payload="virus"
        )
        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

        ev_valid = WriterEvent(
            type="wf-date-change",
            instancePath=parse_instance_path("root:0"),
            payload="2019-11-23"
        )
        self.ed.transform(ev_valid)
        assert ev_valid.payload == "2019-11-23"

    def test_range_change(self) -> None:
        ev_invalid = WriterEvent(
            type="wf-range-change",
            instancePath=parse_instance_path("root:0"),
            payload="virus"
        )
        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

        ev_valid = WriterEvent(
            type="wf-range-change",
            instancePath=parse_instance_path("root:0"),
            payload=[10,42]
        )
        self.ed.transform(ev_valid)
        assert ev_valid.payload == [10, 42]

    def test_time_change(self) -> None:
        ev_invalid = WriterEvent(
            type="wf-time-change",
            instancePath=parse_instance_path("root:0"),
            payload="virus"
        )
        with pytest.raises(RuntimeError):
            self.ed.transform(ev_invalid)

        ev_valid = WriterEvent(
            type="wf-time-change",
            instancePath=parse_instance_path("root:0"),
            payload="23:59"
        )
        self.ed.transform(ev_valid)
        assert ev_valid.payload == "23:59"

    def test_dataframe_update(self) -> None:

        """
        Test that a dataframe update event should decode big int format from frontend
        """
        ev = WriterEvent(
            type="wf-dataframe-update",
            instancePath=parse_instance_path("root:0"),
            payload={
                "record": {
                    "number": 1,
                    "text": "one",
                    "empty_text": ""
                }
            }
        )

        self.ed.transform(ev)

        assert ev.payload['record']['number'] == 1
        assert ev.payload['record']['text'] == "one"

        """
        Test that a dataframe update event should decode big int format from frontend
        """
        ev = WriterEvent(
            type="wf-dataframe-update",
            instancePath=parse_instance_path("root:0"),
            payload={
                "record": {
                    "number": "1n",
                    "text": "one"
                }
            }
        )

        self.ed.transform(ev)

        assert ev.payload['record']['number'] == 1
        assert ev.payload['record']['text'] == "one"

        """
        Test that a dataframe update event should decode big int format from frontend
        """
        ev = WriterEvent(
            type="wf-dataframe-update",
            instancePath=parse_instance_path("root:0"),
            payload={
                "record": {
                    "number": r"1\n",
                    "text": "one"
                }
            }
        )

        self.ed.transform(ev)

        assert ev.payload['record']['number'] == "1n"
        assert ev.payload['record']['text'] == "one"


class TestSessionManager:

    sm = SessionManager()
    proposed_session_id = "c13a280fe17ec663047ec14de15cd93ad686fecf5f9a4dbf262d3a86de8cb577"

    def test_get_new_session_proposed(self) -> None:
        self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example.com"},
            self.proposed_session_id
        )
        self.sm.get_session(self.proposed_session_id)
        s = self.sm.get_session(self.proposed_session_id)
        assert s.cookies == {"testCookie": "yes"}
        assert s.headers == {"origin": "example.com"}
        assert s.session_id == self.proposed_session_id
        assert self.sm.get_session(self.proposed_session_id) == s

    def test_get_new_session_generate_id(self) -> None:
        s = self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example.com"},
            None
        )
        assert s.cookies == {"testCookie": "yes"}
        assert s.headers == {"origin": "example.com"}
        assert s.session_id is not None
        assert self.sm.get_session(s.session_id) == s

    def test_close_session(self) -> None:
        s = self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example.com"},
            None
        )
        self.sm.close_session(s.session_id)
        assert self.sm.get_session(s.session_id) is None

    def test_session_timeout(self) -> None:
        s = self.sm.get_new_session(
            {"testCookie": "yes"},
            {"origin": "example.com"},
            None
        )
        self.sm.prune_sessions()
        assert self.sm.get_session(s.session_id) is not None
        EXCESS_IDLE_SECONDS = 600
        s.last_active_timestamp -= (
            SessionManager.IDLE_SESSION_MAX_SECONDS + EXCESS_IDLE_SECONDS)
        self.sm.prune_sessions()
        assert self.sm.get_session(s.session_id) is None


class TestEditableDataFrame:

    def test_editable_dataframe_expose_pandas_dataframe_as_df_property(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        edf = wf.EditableDataFrame(df)
        assert edf.df is not None
        assert isinstance(edf.df, pandas.DataFrame)

    def test_editable_dataframe_register_mutation_when_df_is_updated(self) -> None:
        # Given
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        edf = wf.EditableDataFrame(df)

        # When
        edf.df.loc[0, "age"] = 26
        edf.df = edf.df

        # Then
        assert edf.mutated() is True

    def test_editable_dataframe_should_read_record_as_dict_based_on_record_index(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })
        edf = wf.EditableDataFrame(df)

        # When
        r = edf.record(0)

        # Then
        assert r['name'] == 'Alice'
        assert r['age'] == 25

    def test_editable_dataframe_should_read_record_as_dict_based_on_record_index_when_dataframe_has_index(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })
        df = df.set_index('name')

        edf = wf.EditableDataFrame(df)

        # When
        r = edf.record(0)

        # Then
        assert r['name'] == 'Alice'
        assert r['age'] == 25

    def test_editable_dataframe_should_read_record_as_dict_based_on_record_index_when_dataframe_has_multi_index(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["Paris", "London", "New York"]
        })
        df = df.set_index(['name', 'city'])

        edf = wf.EditableDataFrame(df)

        # When
        r = edf.record(0)

        # Then
        assert r['name'] == 'Alice'
        assert r['age'] == 25
        assert r['city'] == 'Paris'

    def test_editable_dataframe_should_process_new_record_into_dataframe(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        edf = wf.EditableDataFrame(df)

        # When
        edf.record_add({"record": {"name": "David", "age": 40}})

        # Then
        assert len(edf.df) == 4
        assert edf.df.index.tolist()[3] == 3

    def test_editable_dataframe_should_process_new_record_into_dataframe_with_index(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })
        df = df.set_index('name')

        edf = wf.EditableDataFrame(df)

        # When
        edf.record_add({"record": {"name": "David", "age": 40}})

        # Then
        assert len(edf.df) == 4

    def test_editable_dataframe_should_process_new_record_into_dataframe_with_multiindex(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["Paris", "London", "New York"]
        })
        df = df.set_index(['name', 'city'])

        edf = wf.EditableDataFrame(df)

        # When
        edf.record_add({"record": {"name": "David", "age": 40, "city": "Berlin"}})

        # Then
        assert len(edf.df) == 4

    def test_editable_dataframe_should_update_existing_record_as_dateframe_with_multiindex(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["Paris", "London", "New York"]
        })

        df = df.set_index(['name', 'city'])

        edf = wf.EditableDataFrame(df)

        # When
        edf.record_update({"record_index": 0, "record": {"name": "Alicia", "age": 25, "city": "Paris"}})

        # Then
        assert edf.df.iloc[0]['age'] == 25

    def test_editable_dataframe_should_remove_existing_record_as_dateframe_with_multiindex(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["Paris", "London", "New York"]
        })

        df = df.set_index(['name', 'city'])

        edf = wf.EditableDataFrame(df)

        # When
        edf.record_remove({"record_index": 0})

        # Then
        assert len(edf.df) == 2

    def test_editable_dataframe_should_serialize_pandas_dataframe_with_multiindex(self) -> None:
        df = pandas.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["Paris", "London", "New York"]
        })
        df = df.set_index(['name', 'city'])

        edf = wf.EditableDataFrame(df)

        # When
        table = edf.pyarrow_table()

        # Then
        assert len(table) == 3

    def test_editable_dataframe_expose_polar_dataframe_in_df_property(self) -> None:
        df = polars.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        edf = wf.EditableDataFrame(df)
        assert edf.df is not None
        assert isinstance(edf.df, polars.DataFrame)

    def test_editable_dataframe_should_read_record_from_polar_as_dict_based_on_record_index(self) -> None:
        df = polars.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })
        edf = wf.EditableDataFrame(df)

        # When
        r = edf.record(0)

        # Then
        assert r['name'] == 'Alice'
        assert r['age'] == 25

    def test_editable_dataframe_should_process_new_record_into_polar_dataframe(self) -> None:
        df = polars.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        edf = wf.EditableDataFrame(df)

        # When
        edf.record_add({"record": {"name": "David", "age": 40}})

        # Then
        assert len(edf.df) == 4

    def test_editable_dataframe_should_update_existing_record_into_polar_dataframe(self) -> None:
        df = polars.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        edf = wf.EditableDataFrame(df)

        # When
        edf.record_update({"record_index": 0, "record": {"name": "Alicia", "age": 25}})

        # Then
        assert edf.df[0, "name"] == "Alicia"

    def test_editable_dataframe_should_remove_existing_record_into_polar_dataframe(self) -> None:
        df = polars.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        })

        edf = wf.EditableDataFrame(df)

        # When
        edf.record_remove({"record_index": 0})

        # Then
        assert len(edf.df) == 2

    def test_editable_dataframe_should_serialize_polar_dataframe(self) -> None:
        df = polars.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["Paris", "London", "New York"]
        })

        edf = wf.EditableDataFrame(df)

        # When
        table = edf.pyarrow_table()

        # Then
        assert len(table) == 3


    def test_editable_dataframe_expose_list_of_records_in_df_property(self) -> None:
        records = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35}
        ]

        edf = wf.EditableDataFrame(records)

        assert edf.df is not None
        assert isinstance(edf.df, list)

    def test_editable_dataframe_should_read_record_from_list_of_record_as_dict_based_on_record_index(self) -> None:
        records = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35}
        ]

        edf = wf.EditableDataFrame(records)

        # When
        r = edf.record(0)

        # Then
        assert r['name'] == 'Alice'
        assert r['age'] == 25

    def test_editable_dataframe_should_process_new_record_into_list_of_records(self) -> None:
        records = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35}
        ]

        edf = wf.EditableDataFrame(records)

        # When
        edf.record_add({"record": {"name": "David", "age": 40}})

        # Then
        assert len(edf.df) == 4


    def test_editable_dataframe_should_update_existing_record_into_list_of_record(self) -> None:
        records = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35}
        ]

        edf = wf.EditableDataFrame(records)

        # When
        edf.record_update({"record_index": 0, "record": {"name": "Alicia", "age": 25}})

        # Then
        assert edf.df[0]['name'] == "Alicia"

    def test_editable_dataframe_should_remove_existing_record_into_list_of_record(self) -> None:
        records = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35}
        ]

        edf = wf.EditableDataFrame(records)

        # When
        edf.record_remove({"record_index": 0})

        # Then
        assert len(edf.df) == 2


    def test_editable_dataframe_should_serialized_list_of_records_into_pyarrow_table(self) -> None:
        records = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35}
        ]

        edf = wf.EditableDataFrame(records)

        # When
        table = edf.pyarrow_table()

        # Then
        assert len(table) == 3


def test_import_failure_returns_expected_value_when_import_fails():
    """
    Test that an import failure returns the expected value
    """
    @import_failure(rvalue=False)
    def myfunc():
        import yop

    assert myfunc() is False


def test_import_failure_do_nothing_when_import_go_well():
    """
    Test that the import_failure decorator do nothing when the import is a success
    """
    @import_failure(rvalue=False)
    def myfunc():
        import math
        return 2

    assert myfunc() == 2

