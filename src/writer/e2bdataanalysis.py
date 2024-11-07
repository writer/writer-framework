import os
import json
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import base64
from e2b import DataAnalysis
from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class E2BDataAnalysisIntegration(WorkflowBlock):
    def __init__(self):
        super().__init__()
        self.session = None
    
    @classmethod
    def register(cls, type: str):
        super(E2BDataAnalysisIntegration, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "E2B Data Analysis Integration",
                "description": "Execute data analysis code in a secure sandbox environment",
                "category": "Analysis",
                "fields": {
                    "api_key": {
                        "name": "API Key",
                        "type": "Text",
                        "description": "Your E2B API key"
                    },
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            "execute_code": "Execute Code",
                            "install_package": "Install Package",
                            "upload_file": "Upload File",
                            "download_file": "Download File",
                            "list_files": "List Files",
                            "get_environment_info": "Get Environment Info",
                            "interrupt_execution": "Interrupt Execution",
                            "cleanup_session": "Cleanup Session"
                        },
                        "default": "execute_code"
                    },
                    "code": {
                        "name": "Code",
                        "type": "Text",
                        "description": "Python code to execute",
                        "control": "Textarea",
                        "required": False
                    },
                    "package_name": {
                        "name": "Package Name",
                        "type": "Text",
                        "description": "Name of the Python package to install",
                        "required": False
                    },
                    "file_path": {
                        "name": "File Path",
                        "type": "Text",
                        "description": "Path for file operations",
                        "required": False
                    },
                    "content": {
                        "name": "Content",
                        "type": "Text",
                        "description": "Content for file operations",
                        "required": False
                    },
                    "timeout": {
                        "name": "Timeout",
                        "type": "Text",
                        "description": "Timeout in seconds",
                        "default": "30",
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
                        "description": "An error occurred during execution.",
                        "style": "error",
                    },
                    "timeout": {
                        "name": "Timeout",
                        "description": "The operation timed out.",
                        "style": "error",
                    }
                },
            }
        ))

    async def _initialize_session(self, api_key: str):
        """Initialize E2B session"""
        if not self.session:
            self.session = await DataAnalysis(api_key=api_key)
        return self.session

    async def _execute_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Python code in sandbox"""
        try:
            result = await self.session.execute_python(
                code=code,
                timeout=timeout
            )
            return {
                "output": result.output,
                "error": result.error if result.error else None,
                "duration": result.duration
            }
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Code execution error: {str(e)}")

    async def _install_package(self, package_name: str) -> Dict[str, Any]:
        """Install Python package in sandbox"""
        try:
            result = await self.session.install_python_package(package_name)
            return {
                "package": package_name,
                "status": "installed",
                "output": result
            }
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Package installation error: {str(e)}")

    async def _upload_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Upload file to sandbox"""
        try:
            await self.session.upload_file(file_path, content)
            return {
                "status": "uploaded",
                "file_path": file_path
            }
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"File upload error: {str(e)}")

    async def _download_file(self, file_path: str) -> Dict[str, Any]:
        """Download file from sandbox"""
        try:
            content = await self.session.download_file(file_path)
            return {
                "content": content,
                "file_path": file_path
            }
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"File download error: {str(e)}")

    async def _list_files(self, path: str = ".") -> Dict[str, Any]:
        """List files in sandbox directory"""
        try:
            files = await self.session.list_files(path)
            return {
                "files": files
            }
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"File listing error: {str(e)}")

    async def _get_environment_info(self) -> Dict[str, Any]:
        """Get information about the sandbox environment"""
        try:
            python_version = await self._execute_code("import sys; print(sys.version)")
            installed_packages = await self._execute_code("!pip list")
            
            return {
                "python_version": python_version["output"],
                "installed_packages": installed_packages["output"]
            }
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Environment info error: {str(e)}")

    async def run(self):
        try:
            # Get required fields
            api_key = self._get_field("api_key")
            operation = self._get_field("operation")

            # Initialize session
            await self._initialize_session(api_key)

            # Get optional fields
            code = self._get_field("code", True)
            package_name = self._get_field("package_name", True)
            file_path = self._get_field("file_path", True)
            content = self._get_field("content", True)
            timeout = int(self._get_field("timeout", True, "30"))

            # Execute the requested operation
            if operation == "execute_code":
                if not code:
                    raise ValueError("Code is required for execution")
                result = await self._execute_code(code, timeout)
            
            elif operation == "install_package":
                if not package_name:
                    raise ValueError("Package name is required for installation")
                result = await self._install_package(package_name)
            
            elif operation == "upload_file":
                if not file_path or not content:
                    raise ValueError("File path and content are required for upload")
                result = await self._upload_file(file_path, content)
            
            elif operation == "download_file":
                if not file_path:
                    raise ValueError("File path is required for download")
                result = await self._download_file(file_path)
            
            elif operation == "list_files":
                result = await self._list_files(file_path if file_path else ".")
            
            elif operation == "get_environment_info":
                result = await self._get_environment_info()
            
            elif operation == "cleanup_session":
                if self.session:
                    await self.session.close()
                    self.session = None
                result = {"status": "cleaned"}
            
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            # Store the result and set success outcome
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
            raise e

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None
