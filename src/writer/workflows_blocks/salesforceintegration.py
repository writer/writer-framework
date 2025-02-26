import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError, SalesforceAuthenticationFailed
import pandas as pd
import requests

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class SalesforceIntegration(WorkflowBlock):
    def __init__(self):
        super().__init__()
        self.sf = None
        
    @classmethod
    def register(cls, type: str):
        super(SalesforceIntegration, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Salesforce Integration",
                "description": "Execute Salesforce operations and manage data",
                "category": "CRM",
                "fields": {
                    "username": {
                        "name": "Username",
                        "type": "Text",
                        "description": "Salesforce username"
                    },
                    "password": {
                        "name": "Password",
                        "type": "Text",
                        "description": "Salesforce password"
                    },
                    "security_token": {
                        "name": "Security Token",
                        "type": "Text",
                        "description": "Salesforce security token"
                    },
                    "domain": {
                        "name": "Domain",
                        "type": "Text",
                        "description": "Salesforce domain (test/production)",
                        "options": {
                            "login": "Production",
                            "test": "Sandbox"
                        },
                        "default": "login"
                    },
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            # Query Operations
                            "soql_query": "SOQL Query",
                            "describe_object": "Describe Object",
                            
                            # Record Operations
                            "create_record": "Create Record",
                            "update_record": "Update Record",
                            "delete_record": "Delete Record",
                            "upsert_record": "Upsert Record",
                            
                            # Bulk Operations
                            "bulk_create": "Bulk Create",
                            "bulk_update": "Bulk Update",
                            "bulk_delete": "Bulk Delete",
                            "bulk_upsert": "Bulk Upsert",
                            
                            # Metadata Operations
                            "get_metadata": "Get Metadata",
                            "update_metadata": "Update Metadata",
                            
                            # File Operations
                            "upload_file": "Upload File",
                            "download_file": "Download File"
                        },
                        "default": "soql_query"
                    },
                    "object_name": {
                        "name": "Object Name",
                        "type": "Text",
                        "description": "Salesforce object name (e.g., Account, Contact)",
                        "required": False
                    },
                    "record_id": {
                        "name": "Record ID",
                        "type": "Text",
                        "description": "Salesforce record ID",
                        "required": False
                    },
                    "data": {
                        "name": "Data",
                        "type": "Key-Value",
                        "description": "Data for create/update operations",
                        "default": "{}",
                        "required": False
                    },
                    "query": {
                        "name": "Query",
                        "type": "Text",
                        "description": "SOQL query string",
                        "required": False
                    },
                    "external_id_field": {
                        "name": "External ID Field",
                        "type": "Text",
                        "description": "Field name for upsert operations",
                        "required": False
                    },
                    "batch_size": {
                        "name": "Batch Size",
                        "type": "Text",
                        "description": "Size of batches for bulk operations",
                        "default": "200",
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
                    }
                },
            }
        ))

    def _connect(self, username: str, password: str, security_token: str, domain: str):
        """Establish connection to Salesforce"""
        try:
            self.sf = Salesforce(
                username=username,
                password=password,
                security_token=security_token,
                domain=domain
            )
        except SalesforceAuthenticationFailed as e:
            self.outcome = "auth_error"
            raise RuntimeError(f"Authentication failed: {str(e)}")
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Connection error: {str(e)}")

    def _execute_soql_query(self, query: str) -> Dict[str, Any]:
        """Execute SOQL query"""
        try:
            results = self.sf.query_all(query)
            return {
                "total_size": results['totalSize'],
                "records": results['records']
            }
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Query error: {str(e)}")

    def _describe_object(self, object_name: str) -> Dict[str, Any]:
        """Get object metadata"""
        try:
            obj = getattr(self.sf, object_name)
            metadata = obj.describe()
            return metadata
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Describe error: {str(e)}")

    def _create_record(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        try:
            obj = getattr(self.sf, object_name)
            result = obj.create(data)
            return result
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Create error: {str(e)}")

    def _update_record(self, object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record"""
        try:
            obj = getattr(self.sf, object_name)
            result = obj.update(record_id, data)
            return result
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Update error: {str(e)}")

    def _delete_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record"""
        try:
            obj = getattr(self.sf, object_name)
            result = obj.delete(record_id)
            return result
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Delete error: {str(e)}")

    def _upsert_record(self, object_name: str, external_id_field: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert a record using external ID"""
        try:
            obj = getattr(self.sf, object_name)
            result = obj.upsert(external_id_field, data)
            return result
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Upsert error: {str(e)}")

    def _bulk_operation(self, operation: str, object_name: str, data: List[Dict[str, Any]], 
                       batch_size: int = 200) -> Dict[str, Any]:
        """Execute bulk operation"""
        try:
            results = []
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                if operation == "create":
                    result = getattr(self.sf.bulk, object_name).insert(batch)
                elif operation == "update":
                    result = getattr(self.sf.bulk, object_name).update(batch)
                elif operation == "delete":
                    result = getattr(self.sf.bulk, object_name).delete(batch)
                elif operation == "upsert":
                    result = getattr(self.sf.bulk, object_name).upsert(batch)
                
                results.extend(result)
            
            return {
                "total_processed": len(results),
                "results": results
            }
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Bulk operation error: {str(e)}")

    def run(self):
        try:
            # Get authentication fields
            username = self._get_field("username")
            password = self._get_field("password")
            security_token = self._get_field("security_token")
            domain = self._get_field("domain", False, "login")

            # Connect to Salesforce
            self._connect(username, password, security_token, domain)

            # Get operation details
            operation = self._get_field("operation")
            object_name = self._get_field("object_name", True)
            record_id = self._get_field("record_id", True)
            data = self._get_field("data", True, "{}")
            query = self._get_field("query", True)
            external_id_field = self._get_field("external_id_field", True)
            batch_size = int(self._get_field("batch_size", True, "200"))

            # Parse data if provided
            if data:
                data = json.loads(data)

            # Execute requested operation
            if operation == "soql_query":
                if not query:
                    raise ValueError("Query is required for SOQL operation")
                result = self._execute_soql_query(query)
                
            elif operation == "describe_object":
                if not object_name:
                    raise ValueError("Object name is required for describe operation")
                result = self._describe_object(object_name)
                
            elif operation == "create_record":
                if not object_name or not data:
                    raise ValueError("Object name and data are required for create operation")
                result = self._create_record(object_name, data)
                
            elif operation == "update_record":
                if not object_name or not record_id or not data:
                    raise ValueError("Object name, record ID, and data are required for update operation")
                result = self._update_record(object_name, record_id, data)
                
            elif operation == "delete_record":
                if not object_name or not record_id:
                    raise ValueError("Object name and record ID are required for delete operation")
                result = self._delete_record(object_name, record_id)
                
            elif operation == "upsert_record":
                if not object_name or not external_id_field or not data:
                    raise ValueError("Object name, external ID field, and data are required for upsert operation")
                result = self._upsert_record(object_name, external_id_field, data)
                
            elif operation in ["bulk_create", "bulk_update", "bulk_delete", "bulk_upsert"]:
                if not object_name or not data:
                    raise ValueError("Object name and data are required for bulk operations")
                result = self._bulk_operation(
                    operation.replace("bulk_", ""),
                    object_name,
                    data if isinstance(data, list) else [data],
                    batch_size
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

