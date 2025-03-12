import os

import pytest
from writer.blocks.airtablequeryrecords import AirtableQueryRecords

from backend_external.fixtures import airtable_fixture

WRITER_CI_TEST_AIRTABLE_API_KEY=os.getenv("WRITER_CI_TEST_AIRTABLE_API_KEY")
WRITER_CI_TEST_AIRTABLE_BASE=os.getenv("WRITER_CI_TEST_AIRTABLE_BASE")
WRITER_CI_TEST_AIRTABLE_TABLE=os.getenv("WRITER_CI_TEST_AIRTABLE_TABLE")


@pytest.fixture(scope="module", autouse=True)
def init_airtable_table():
    records = {
        "recXqy7djJEOGZwdf": {"Name": "Fabien", "Ville": "Paris", "Age": 31},
        "recxqVXoPMl2QVs8i": {"Name": "Ramiro", "Ville": "Warsaw", "Age": 32},
        "recRYlOBqOOYLvUEm": {"Name": "Fabien", "Ville": "Lyon", "Age": 33},
    }

    airtable_fixture.prepare_records(api_key=WRITER_CI_TEST_AIRTABLE_API_KEY,
                                     base=WRITER_CI_TEST_AIRTABLE_BASE,
                                     table=WRITER_CI_TEST_AIRTABLE_TABLE,
                                     expected_records=records)


def test_airtable_query_records_success(session, runner):
    if not WRITER_CI_TEST_AIRTABLE_API_KEY or not WRITER_CI_TEST_AIRTABLE_BASE or not WRITER_CI_TEST_AIRTABLE_TABLE:
        pytest.skip("Airtable API key not provided")

    formula = "{Name}='Fabien'"

    # Create a fake component with necessary fields
    session.add_fake_component({
        "apiKey": WRITER_CI_TEST_AIRTABLE_API_KEY,
        "base": WRITER_CI_TEST_AIRTABLE_BASE,
        "table": WRITER_CI_TEST_AIRTABLE_TABLE,
        "formula": formula
    })

    # Initialize the AirtableQueryRecords block
    block = AirtableQueryRecords("fake_id", runner, {})

    # Run the block
    block.run()

    # Assertions
    assert block.outcome == "success"
    assert isinstance(block.result, list)
    assert len(block.result) == 2

def test_airtable_query_records_success_with_multiple_sorts(session, runner):
    if not WRITER_CI_TEST_AIRTABLE_API_KEY or not WRITER_CI_TEST_AIRTABLE_BASE or not WRITER_CI_TEST_AIRTABLE_TABLE:
        pytest.skip("Airtable API key not provided")

    sort_fields = '[{"field": "Age", "direction": "desc"}]'

    # Create a fake component with necessary fields
    session.add_fake_component({
        "apiKey": WRITER_CI_TEST_AIRTABLE_API_KEY,
        "base": WRITER_CI_TEST_AIRTABLE_BASE,
        "table": WRITER_CI_TEST_AIRTABLE_TABLE,
        "sortFields": sort_fields
    })

    # Initialize the AirtableQueryRecords block
    block = AirtableQueryRecords("fake_id", runner, {})

    # Run the block
    block.run()

    # Assertions
    assert block.outcome == "success"
    assert isinstance(block.result, list)
    assert len(block.result) == 3
    assert block.result[0]["fields"]["Age"] == 33
    assert block.result[0]["fields"]["Name"] == "Fabien"

def test_airtable_query_records_missing_api_key(session, runner):
    if not WRITER_CI_TEST_AIRTABLE_API_KEY or not WRITER_CI_TEST_AIRTABLE_BASE or not WRITER_CI_TEST_AIRTABLE_TABLE:
        pytest.skip("Airtable API key not provided")

    session.add_fake_component({
        "base": WRITER_CI_TEST_AIRTABLE_BASE,
        "table": WRITER_CI_TEST_AIRTABLE_TABLE
    })

    # Initialize the AirtableQueryRecords block
    block = AirtableQueryRecords("fake_id", runner, {})

    # Run the block and expect an error
    with pytest.raises(Exception) as excinfo:
        block.run()

    # Assertions
    assert block.outcome == "error"
    assert "apiKey" in str(excinfo.value)

def test_airtable_query_records_invalid_base(session, runner):
    if not WRITER_CI_TEST_AIRTABLE_API_KEY or not WRITER_CI_TEST_AIRTABLE_BASE or not WRITER_CI_TEST_AIRTABLE_TABLE:
        pytest.skip("Airtable API key not provided")

    session.add_fake_component({
        "apiKey": WRITER_CI_TEST_AIRTABLE_API_KEY,
        "base": "invalid_base",
        "table": WRITER_CI_TEST_AIRTABLE_TABLE
    })

    # Initialize the AirtableQueryRecords block
    block = AirtableQueryRecords("fake_id", runner, {})

    # Run the block and expect an error
    with pytest.raises(Exception) as excinfo:
        block.run()

    # Assertions
    assert block.outcome == "error"
    assert "404 client error" in str(excinfo.value).lower()
