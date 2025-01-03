from typing import List

import requests


def records(api_key: str, base: str, table: str) -> List[dict]:
    """
    >>> records = airtable_fixture.records("pka.....", "app.....", "Table")
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = f"https://api.airtable.com/v0/{base}/{table}"
    response = requests.get(url, headers=headers)
    return response.json()

def create_record(api_key: str, base: str, table: str, fields: dict) -> dict:
    """
    >>> record = airtable_fixture.create_record("pka.....", "app.....", "Table", {"Name": "John Doe", "Age": 30})
    >>> print(record["id"])
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = f"https://api.airtable.com/v0/{base}/{table}"
    payload = {"fields": fields}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def update_record(api_key: str, base :str, table: str, record_id: str, fields: dict) -> dict:
    """
    >>> record = airtable_fixture.update_record("pka.....", "app.....", "Table", "rec.....", {"Age": 31})
    >>> print(record["id"])
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = f"https://api.airtable.com/v0/{base}/{table}/{record_id}"
    payload = {"fields": fields}
    response = requests.patch(url, json=payload, headers=headers)
    return response.json()


def remove_record(api_key: str, base: str, table: str, record_id: str) -> dict:
    """
    >>> record = airtable_fixture.remove_record("pka.....", "app.....", "Table", "rec.....")
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = f"https://api.airtable.com/v0/{base}/{table}/{record_id}"
    response = requests.delete(url, headers=headers)
    return response.json()

def prepare_records(api_key: str, base: str, table: str, expected_records: dict):
    """
    * delete records that are not in expected records
    * updates records that differ from expected_records
    * throws an exception if a record from expected_records is not found in Airtable
    """
    if not api_key or not base or not table:
        return

    _records = records(api_key, base, table)
    for record in _records["records"]:
        if record["id"] not in expected_records.keys():
            remove_record(api_key, base, table, record["id"])
            continue

        if record["fields"] != expected_records[record["id"]]:
            update_record(api_key, base, table, record["id"])

    expected_record_ids = set(expected_records.keys())
    records_ids = {record["id"] for record in _records["records"]}
    for record_id in expected_record_ids - records_ids:
        raise ValueError(f"Corruption: record with ID {record_id} not found in Airtable")
