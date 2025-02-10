

import json
import math
from pathlib import Path

import altair
import numpy as np
import pandas as pd
import polars
import pyarrow
import pytest
import plotly.express as px
import urllib

from writer import serializer
import writer
from writer.core import BytesWrapper, FileWrapper


test_app_dir = Path(__file__).resolve().parent / "basic_test_app"

class TestFileWrapper():

    file_path = str(test_app_dir / "assets/myfile.csv")

    def test_get_as_dataurl(self) -> None:
        fw = FileWrapper(self.file_path, "text/plain")
        assert fw.get_as_dataurl() == "data:text/plain;base64,aGVsbG8gd29ybGQ="


class TestBytesWrapper():

    def test_get_as_dataurl(self) -> None:
        bw = BytesWrapper("hello world".encode("utf-8"), "text/plain")
        assert bw.get_as_dataurl() == "data:text/plain;base64,aGVsbG8gd29ybGQ="


class TestStateSerializer():

    file_path = str(test_app_dir / "assets/myfile.csv")
    df_path = str(test_app_dir / "assets/main_df.csv")

    def test_nested_dict(self) -> None:
        d = {
            "features": {
                "eyes": "green"
            }
        }
        s = serializer.serialize(d)
        assert s.get("features").get("eyes") == "green"

    def test_non_str_keys_in_dict(self) -> None:
        d = {
            ("tuple", "key"): "Invalid"
        }
        s = serializer.serialize(d)
        assert s.get("('tuple', 'key')") is not None

    def test_bytes(self) -> None:
        d = {
            "name": "Normal name",
            "data": "hello world".encode("utf-8")
        }
        s = serializer.serialize(d)

        # Note absence of MIME type

        assert s.get("data") == "data:;base64,aGVsbG8gd29ybGQ="

    def test_wrappers(self) -> None:
        fw = FileWrapper(self.file_path, "text/plain")
        bw = BytesWrapper("hello world".encode("utf-8"), "text/plain")
        d = {
            "datafw": fw,
            "databw": bw
        }
        s = serializer.serialize(d)
        assert s.get("datafw") == s.get("databw")
        assert s.get("databw") == "data:text/plain;base64,aGVsbG8gd29ybGQ="

    def test_numbers(self) -> None:
        d = {
            "name": "Normal name",
            "pet_count": 2,
            "fav_number": math.nan,
            "likes_coffee": True,
            "likes_black_tea": False
        }
        s = serializer.serialize(d)
        assert s.get("name") == "Normal name"
        assert s.get("pet_count") == 2
        assert s.get("fav_number") is None  # NaN is serialised as None
        assert s.get("likes_coffee") == True
        assert s.get("likes_black_tea") == False

    def test_invalid(self) -> None:

        # A Python module is used as an example of a non-serialisable object

        d = {
            "fav_module": writer
        }

        s = serializer.serialize(d)
        assert s.get("fav_module").endswith("cannot be serialized.")

    def test_numpy_array_and_int(self) -> None:
        d = {
            "counter": 0,
            "np_a": np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
        }
        s = serializer.serialize(d)
        assert s.get("np_a")[0][1] == 2
        json.dumps(s)

    def test_numpy_array_with_complex(self) -> None:
        d = {
            "counter": 0,
            "np_a": np.array([[1, 2, 3+3j], [4, 5, 6], [7, 8, 9]]),
        }
        s = serializer.serialize(d)
        assert s.get("np_a")[0][2].endswith("cannot be serialized.")

    def test_nans_in_dataframe(self) -> None:
        data = {
            "column_a": [1, 2, np.nan, 4],
            "column_b": [5, np.nan, 7, 8],
        }
        d = {
            "name": "Normal name",
            "df": pd.DataFrame(data)
        }
        s = serializer.serialize(d)

    def test_unserialisable_altair(self) -> None:
        chart = altair.Chart([3, 3, 3]).mark_line().encode(
            x='x',
            y='y'
        )
        d = {
            "chart": chart
        }
        with pytest.warns(UserWarning):
            with pytest.raises(ValueError):
                s = serializer.serialize(d)
                
    def test_plotly_should_be_serialize_to_json(self) -> None:
        """
        Test that plotly figure should be serialised to json string directly. Serializing the json directly allows you 
        to display datasets that exceed 10,000 records. 
        
        With the default json serializer, a dataset like this blows up memory. Plotly is using internaly orjson as serializer.
        """
        # Arrange
        df = px.data.iris()
        fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species", symbol="species")
        
        # Acts
        json_code = serializer.serialize(fig)

        # Assert
        assert isinstance(json_code, str)
        o = json.loads(json_code)
        assert 'data' in o
        assert 'layout' in o

    def test_pandas_df(self) -> None:
        d = {
            "name": "Normal name",
            "df": pd.read_csv(self.df_path)
        }
        s = serializer.serialize(d)
        assert s.get("name") == "Normal name"
        df_durl = s.get("df")
        df_buffer = urllib.request.urlopen(df_durl)
        reader = pyarrow.ipc.open_file(df_buffer)
        table = reader.read_all()
        assert table.column("name")[0].as_py() == "Byte"
        assert table.column("length_cm")[2].as_py() == 32

    def test_polars_df(self) -> None:
        d = {
            "name": "Normal name",
            "df": polars.read_csv(self.df_path)
        }
        s = serializer.serialize(d)
        assert s.get("name") == "Normal name"
        df_durl = s.get("df")
        df_buffer = urllib.request.urlopen(df_durl)
        reader = pyarrow.ipc.open_file(df_buffer)
        table = reader.read_all()
        assert table.column("name")[0].as_py() == "Byte"
        assert table.column("length_cm")[2].as_py() == 32