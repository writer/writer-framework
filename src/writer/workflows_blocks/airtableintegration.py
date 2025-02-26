import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import requests
from ratelimit import limits, sleep_and_retry
import pandas as pd
from urllib.parse import quote

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class AirtableIntegration(WorkflowBlock):
    BASE_URL = "https://api.airtable.com/v0"
    METADATA_URL = "https://api.airtable.com/v0/meta"
    # Rate limit: 5 requests per second
    CALLS_PER_SECOND = 5
    
    def __init__(self):
        super().__init__()
        self.session = None
        
    @classmethod
    def register(cls, type: str):
        super(AirtableIntegration, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Airtable Integration",
                "description": "Execute Airtable operations and manage bases",
                "category": "Database",
                "fields": {
                    "api_key": {
                        "name": "API Key",
                        "type": "Text",
                        "description": "Your Airtable API key"
                    },
                    "base_id": {
                        "name": "Base ID",
                        "type": "Text",
                        "description": "Airtable base ID"
                    },
                    "table_name": {
                        "name": "Table Name",
                        "type": "Text",
                        "description": "Name of the table",
                        "required": False
                    },
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            # Record Operations
                            "list_records": "List Records",
                            "get_record": "Get Record",
                            "create_record": "Create Record",
                            "update_record": "Update Record",
                            "delete_record": "Delete Record",
                            "batch_create": "Batch Create Records",
                            "batch_update": "Batch Update Records",
                            "batch_delete": "Batch Delete Records",
                            
                            # Table Operations
                            "list_tables": "List Tables",
                            "get_table_schema": "Get Table Schema",
                            "create_table": "Create Table",
                            "update_table": "Update Table",
                            
                            # View Operations
                            "list_views": "List Views",
                            "get_view": "Get View",
                            "create_view": "Create View",
                            
                            # Field Operations
                            "list_fields": "List Fields",
                            "create_field": "Create Field",
                            "update_field": "Update Field",
                            
                            # Automation Operations
                            "list_automations": "List Automations",
                            "run_automation": "Run Automation",
                            
                            # Base Operations
                            "get_base_schema": "Get Base Schema",
                            "get_base_usage": "Get Base Usage"
                        },
                        "default": "list_records"
                    },
                    "record_id": {
                        "name": "Record ID",
                        "type": "Text",
                        "description": "ID of the record to operate on",
                        "required": False
                    },
                    "data": {
                        "name": "Data",
                        "type": "Key-Value",
                        "description": "Data for create/update operations",
                        "default": "{}",
                        "required": False
                    },
                    "view_name": {
                        "name": "View Name",
                        "type": "Text",
                        "description": "Name of the view",
                        "required": False
                    },
                    "formula": {
                        "name": "Formula",
                        "type": "Text",
                        "description": "Airtable formula for filtering",
                        "required": False
                    },
                    "sort_field": {
                        "name": "Sort Field",
                        "type": "Text",
                        "description": "Field to sort by",
                        "required": False
                    },
                    "max_records": {
                        "name": "Max Records",
                        "type": "Text",
                        "description": "Maximum number of records to return",
                        "default": "100",
                        "required": False
                    },
                    "cell_format": {
                        "name": "Cell Format",
                        "type": "Text",
                        "options": {
                            "json": "JSON",
                            "string": "String"
                        },
                        "default": "json",
                        "required": False
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The operation completed successfully.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "An error occurred during the operation.",
                        "style": "error",
                    },
                    "auth_error": {
                        "name": "Authentication Error",
                        "description": "Authentication failed.",
                        "style": "error",
                    },
                    "rate_limit": {
                        "name": "Rate Limit",
                        "description": "Rate limit exceeded.",
                        "style": "error",
                    }
                },
            }
        ))

    def _get_headers(self, api_key: str) -> Dict[str, str]:
        """Create headers for Airtable API requests"""
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    @sleep_and_retry
    @limits(calls=CALLS_PER_SECOND, period=1)
    def _make_request(self, method: str, url: str, headers: Dict[str, str], 
                     data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make rate-limited API request"""
        try:
            response = requests.request(method, url, headers=headers, json=data)
            
            if response.status_code == 429:
                self.outcome = "rate_limit"
                raise RuntimeError("Rate limit exceeded")
            elif response.status_code == 401:
                self.outcome = "auth_error"
                raise RuntimeError("Authentication failed")
            elif response.status_code >= 400:
                self.outcome = "error"
                raise RuntimeError(f"API error: {response.text}")
                
            return response.json()
        except requests.exceptions.RequestException as e:
            self.outcome = "error"
            raise RuntimeError(f"Request error: {str(e)}")

    def _handle_records(self, operation: str, headers: Dict[str, str], base_id: str, 
                       table_name: str, data: Dict[str, Any] = None, 
                       record_id: str = None) -> Dict[str, Any]:
        """Handle record operations"""
        try:
            base_url = f"{self.BASE_URL}/{base_id}/{quote(table_name)}"
            
            if operation == "list_records":
                params = []
                if data.get("view"):
                    params.append(f"view={quote(data['view'])}")
                if data.get("formula"):
                    params.append(f"filterByFormula={quote(data['formula'])}")
                if data.get("sort_field"):
                    params.append(f"sort[0][field]={quote(data['sort_field'])}")
                    params.append(f"sort[0][direction]={data.get('sort_direction', 'asc')}")
                if data.get("max_records"):
                    params.append(f"maxRecords={data['max_records']}")
                
                url = f"{base_url}?{'&'.join(params)}" if params else base_url
                return self._make_request("GET", url, headers)
            
            elif operation == "get_record":
                return self._make_request("GET", f"{base_url}/{record_id}", headers)
            
            elif operation == "create_record":
                return self._make_request("POST", base_url, headers, {"fields": data})
            
            elif operation == "update_record":
                return self._make_request("PATCH", f"{base_url}/{record_id}", 
                                        headers, {"fields": data})
            
            elif operation == "delete_record":
                return self._make_request("DELETE", f"{base_url}/{record_id}", headers)
            
            elif operation.startswith("batch_"):
                batch_operation = operation.split("_")[1]
                method = {
                    "create": "POST",
                    "update": "PATCH",
                    "delete": "DELETE"
                }[batch_operation]
                
                if batch_operation in ["create", "update"]:
                    payload = {"records": [{"fields": record} for record in data]}
                else:  # delete
                    payload = {"records": data}
                    
                return self._make_request(method, f"{base_url}/batch", headers, payload)
            
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Record operation error: {str(e)}")

    def _handle_tables(self, operation: str, headers: Dict[str, str], base_id: str,
                      table_name: str = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle table operations"""
        try:
            if operation == "list_tables":
                url = f"{self.METADATA_URL}/bases/{base_id}/tables"
                return self._make_request("GET", url, headers)
            
            elif operation == "get_table_schema":
                url = f"{self.METADATA_URL}/bases/{base_id}/tables/{quote(table_name)}"
                return self._make_request("GET", url, headers)
            
            elif operation == "create_table":
                url = f"{self.METADATA_URL}/bases/{base_id}/tables"
                return self._make_request("POST", url, headers, data)
            
            elif operation == "update_table":
                url = f"{self.METADATA_URL}/bases/{base_id}/tables/{quote(table_name)}"
                return self._make_request("PATCH", url, headers, data)
            
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Table operation error: {str(e)}")

    def _handle_views(self, operation: str, headers: Dict[str, str], base_id: str,
                     table_name: str, view_name: str = None, 
                     data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle view operations"""
        try:
            base_url = f"{self.METADATA_URL}/bases/{base_id}/tables/{quote(table_name)}/views"
            
            if operation == "list_views":
                return self._make_request("GET", base_url, headers)
            
            elif operation == "get_view":
                return self._make_request("GET", f"{base_url}/{quote(view_name)}", headers)
            
            elif operation == "create_view":
                return self._make_request("POST", base_url, headers, data)
            
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"View operation error: {str(e)}")

    def run(self):
        try:
            # Get authentication and base configuration
            api_key = self._get_field("api_key")
            base_id = self._get_field("base_id")
            headers = self._get_headers(api_key)

            # Get operation details
            operation = self._get_field("operation")
            table_name = self._get_field("table_name", True)
            record_id = self._get_field("record_id", True)
            view_name = self._get_field("view_name", True)
            data = json.loads(self._get_field("data", True, "{}"))

            # Process optional parameters
            if "max_records" in self._fields:
                data["max_records"] = int(self._get_field("max_records", True, "100"))
            if "formula" in self._fields:
                data["formula"] = self._get_field("formula", True)
            if "sort_field" in self._fields:
                data["sort_field"] = self._get_field("sort_field", True)
            if "view" in self._fields:
                data["view"] = self._get_field("view", True)

            # Execute requested operation
            if operation in ["list_records", "get_record", "create_record", 
                           "update_record", "delete_record", "batch_create", 
                           "batch_update", "batch_delete"]:
                result = self._handle_records(
                    operation, headers, base_id, table_name, data, record_id
                )
                
            elif operation in ["list_tables", "get_table_schema", "create_table", 
                             "update_table"]:
                result = self._handle_tables(
                    operation, headers, base_id, table_name, data
                )
                
            elif operation in ["list_views", "get_view", "create_view"]:
                result = self._handle_views(
                    operation, headers, base_id, table_name, view_name, data
                )
                
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            # Store result and set success outcome
            self.result = {
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "data": result
            }
            self.outcome = "success"

        except ValueError as e:
            self.outcome = "error"
            raise RuntimeError(f"Validation error: {str(e)}")
        except Exception as e:
            if not self.outcome:
                self.outcome = "error"
            raise RuntimeError(f"Operation error: {str(e)}")

