import os

import pytest
from writer.blocks.airtablemanipulaterecord import AirtableManipulateRecord

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


def test_airtable_create_record(session, runner):
    if not WRITER_CI_TEST_AIRTABLE_API_KEY or not WRITER_CI_TEST_AIRTABLE_BASE or not WRITER_CI_TEST_AIRTABLE_TABLE:
        pytest.skip("Airtable API key not provided")

    fields = '{"Name": "John Doe", "Age": 30}'
    session.add_fake_component({
        "apiKey": WRITER_CI_TEST_AIRTABLE_API_KEY,
        "base": WRITER_CI_TEST_AIRTABLE_BASE,
        "table": WRITER_CI_TEST_AIRTABLE_TABLE,
        "operation": "create",
        "fields": fields
    })

    block = AirtableManipulateRecord("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert "id" in block.result
    assert "fields" in block.result
    assert block.result["fields"]["Name"] == "John Doe"
    assert block.result["fields"]["Age"] == 30

    airtable_fixture.remove_record(WRITER_CI_TEST_AIRTABLE_API_KEY, WRITER_CI_TEST_AIRTABLE_BASE, WRITER_CI_TEST_AIRTABLE_TABLE, block.result["id"])


def test_airtable_update_record(session, runner):
    if not WRITER_CI_TEST_AIRTABLE_API_KEY or not WRITER_CI_TEST_AIRTABLE_BASE or not WRITER_CI_TEST_AIRTABLE_TABLE:
        pytest.skip("Airtable API key not provided")

    new_fields = '{"Age": 31}'
    existing_record_id = "recXqy7djJEOGZwdf"  # Replace with a valid record ID for your test

    session.add_fake_component({
        "apiKey": WRITER_CI_TEST_AIRTABLE_API_KEY,
        "base": WRITER_CI_TEST_AIRTABLE_BASE,
        "table": WRITER_CI_TEST_AIRTABLE_TABLE,
        "operation": "update",
        "recordId": existing_record_id,
        "fields": new_fields
    })

    block = AirtableManipulateRecord("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"
    assert block.result["id"] == existing_record_id
    assert block.result["fields"]["Age"] == 31

def test_airtable_remove_record(session, runner):
    if not WRITER_CI_TEST_AIRTABLE_API_KEY or not WRITER_CI_TEST_AIRTABLE_BASE or not WRITER_CI_TEST_AIRTABLE_TABLE:
        pytest.skip("Airtable API key not provided")

    record = airtable_fixture.create_record(WRITER_CI_TEST_AIRTABLE_API_KEY, WRITER_CI_TEST_AIRTABLE_BASE, WRITER_CI_TEST_AIRTABLE_TABLE, {"Name": "Test Remove Record"})

    delete_record_id = record["id"]  # Replace with a valid record ID for your test

    session.add_fake_component({
        "apiKey": WRITER_CI_TEST_AIRTABLE_API_KEY,
        "base": WRITER_CI_TEST_AIRTABLE_BASE,
        "table": WRITER_CI_TEST_AIRTABLE_TABLE,
        "operation": "remove",
        "recordId": delete_record_id,
    })

    block = AirtableManipulateRecord("fake_id", runner, {})
    block.run()
    assert block.outcome == "success"

def test_airtable_operation_missing_api_key(session, runner):
    if not WRITER_CI_TEST_AIRTABLE_BASE or not WRITER_CI_TEST_AIRTABLE_TABLE:
        pytest.skip("Airtable API base or table not provided")

    session.add_fake_component({
        "base": WRITER_CI_TEST_AIRTABLE_BASE,
        "table": WRITER_CI_TEST_AIRTABLE_TABLE,
        "operation": "create",
        "fields": '{"Name": "Test Missing API Key"}'
    })

    block = AirtableManipulateRecord("fake_id", runner, {})
    with pytest.raises(Exception) as excinfo:
        block.run()
    assert block.outcome == "error"
    assert "apiKey" in str(excinfo.value)

def test_airtable_operation_invalid_base(session, runner):
    if not WRITER_CI_TEST_AIRTABLE_API_KEY or not WRITER_CI_TEST_AIRTABLE_TABLE:
        pytest.skip("Airtable API key or table not provided")

    session.add_fake_component({
        "apiKey": WRITER_CI_TEST_AIRTABLE_API_KEY,
        "base": "invalid_base",
        "table": WRITER_CI_TEST_AIRTABLE_TABLE,
        "operation": "create",
        "fields": '{"Name": "Test Invalid Base"}'
    })

    block = AirtableManipulateRecord("fake_id", runner, {})
    with pytest.raises(Exception) as excinfo:
        block.run()

    assert block.outcome == "error"
    assert "404 client error" in str(excinfo.value).lower()
