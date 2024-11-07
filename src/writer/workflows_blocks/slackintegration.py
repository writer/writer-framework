import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class SlackIntegration(WorkflowBlock):
    BASE_URL = "https://slack.com/api"
    
    @classmethod
    def register(cls, type: str):
        super(SlackIntegration, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Slack Integration",
                "description": "Executes various Slack API operations for channels, messages, and users.",
                "category": "Collaboration",
                "fields": {
                    "api_token": {
                        "name": "API Token",
                        "type": "Text",
                        "description": "Your Slack API token"
                    },
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            # Channel operations
                            "create_channel": "Create Channel",
                            "list_channels": "List Channels",
                            "join_channel": "Join Channel",
                            "leave_channel": "Leave Channel",
                            
                            # Message operations
                            "post_message": "Post Message",
                            "update_message": "Update Message",
                            "delete_message": "Delete Message",
                            
                            # User operations
                            "list_users": "List Users",
                            "get_user_info": "Get User Info",
                            "get_user_presence": "Get User Presence"
                        },
                        "default": "list_channels"
                    },
                    "channel_id": {
                        "name": "Channel ID",
                        "type": "Text",
                        "description": "ID of the Slack channel to operate on",
                        "required": False
                    },
                    "message_ts": {
                        "name": "Message Timestamp",
                        "type": "Text",
                        "description": "Timestamp of the message to update or delete",
                        "required": False
                    },
                    "message_text": {
                        "name": "Message Text",
                        "type": "Text",
                        "description": "Text content of the message to post or update",
                        "required": False
                    },
                    "user_id": {
                        "name": "User ID",
                        "type": "Text",
                        "description": "ID of the Slack user to retrieve information for",
                        "required": False
                    },
                    "additional_params": {
                        "name": "Additional Parameters",
                        "type": "Key-Value",
                        "description": "Additional parameters for the API operation",
                        "default": "{}",
                        "required": False
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The operation was completed successfully.",
                        "style": "success",
                    },
                    "apiError": {
                        "name": "API Error",
                        "description": "An error occurred while making the API request.",
                        "style": "error",
                    },
                    "authError": {
                        "name": "Authentication Error",
                        "description": "Invalid API token or insufficient permissions.",
                        "style": "error",
                    }
                },
            }
        ))

    def _get_headers(self, api_token: str) -> Dict[str, str]:
        """Create headers for Slack API requests"""
        return {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and set appropriate outcome"""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            self.outcome = "authError"
            raise RuntimeError("Authentication failed: Invalid API token or insufficient permissions")
        else:
            self.outcome = "apiError"
            raise RuntimeError(f"API error: {response.status_code} - {response.text}")

    def _create_channel(self, headers: Dict[str, str], name: str) -> Dict[str, Any]:
        """Create a new Slack channel"""
        url = f"{self.BASE_URL}/conversations.create"
        data = {
            "name": name
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return self._handle_response(response)

    def _list_channels(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """List all Slack channels"""
        url = f"{self.BASE_URL}/conversations.list"
        response = requests.get(url, headers=headers)
        return self._handle_response(response)

    def _join_channel(self, headers: Dict[str, str], channel_id: str) -> Dict[str, Any]:
        """Join a Slack channel"""
        url = f"{self.BASE_URL}/conversations.join"
        data = {
            "channel": channel_id
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return self._handle_response(response)

    def _post_message(self, headers: Dict[str, str], channel_id: str, text: str) -> Dict[str, Any]:
        """Post a message to a Slack channel"""
        url = f"{self.BASE_URL}/chat.postMessage"
        data = {
            "channel": channel_id,
            "text": text
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return self._handle_response(response)

    def _update_message(self, headers: Dict[str, str], channel_id: str, ts: str, text: str) -> Dict[str, Any]:
        """Update a message in a Slack channel"""
        url = f"{self.BASE_URL}/chat.update"
        data = {
            "channel": channel_id,
            "ts": ts,
            "text": text
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return self._handle_response(response)

    def _delete_message(self, headers: Dict[str, str], channel_id: str, ts: str) -> Dict[str, Any]:
        """Delete a message from a Slack channel"""
        url = f"{self.BASE_URL}/chat.delete"
        data = {
            "channel": channel_id,
            "ts": ts
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return self._handle_response(response)

    def _list_users(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """List all Slack users"""
        url = f"{self.BASE_URL}/users.list"
        response = requests.get(url, headers=headers)
        return self._handle_response(response)

    def _get_user_info(self, headers: Dict[str, str], user_id: str) -> Dict[str, Any]:
        """Get information about a Slack user"""
        url = f"{self.BASE_URL}/users.info"
        data = {
            "user": user_id
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return self._handle_response(response)

    def _get_user_presence(self, headers: Dict[str, str], user_id: str) -> Dict[str, Any]:
        """Get the presence status of a Slack user"""
        url = f"{self.BASE_URL}/users.getPresence"
        data = {
            "user": user_id
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return self._handle_response(response)

    def run(self):
        try:
            # Get required fields
            api_token = self._get_field("api_token")
            operation = self._get_field("operation")
            headers = self._get_headers(api_token)

            # Get optional fields
            channel_id = self._get_field("channel_id", True)
            message_ts = self._get_field("message_ts", True)
            message_text = self._get_field("message_text", True)
            user_id = self._get_field("user_id", True)
            additional_params = self._get_field("additional_params", True, "{}")

            # Execute the requested operation
            if operation == "create_channel":
                result = self._create_channel(headers, channel_id)
            elif operation == "list_channels":
                result = self._list_channels(headers)
            elif operation == "join_channel":
                result = self._join_channel(headers, channel_id)
            elif operation == "post_message":
                result = self._post_message(headers, channel_id, message_text)
            elif operation == "update_message":
                result = self._update_message(headers, channel_id, message_ts, message_text)
            elif operation == "delete_message":
                result = self._delete_message(headers, channel_id, message_ts)
            elif operation == "list_users":
                result = self._list_users(headers)
            elif operation == "get_user_info":
                result = self._get_user_info(headers, user_id)
            elif operation == "get_user_presence":
                result = self._get_user_presence(headers, user_id)
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
            self.outcome = "apiError"
            raise RuntimeError(f"Validation error: {str(e)}")
        except requests.exceptions.RequestException as e:
            self.outcome = "apiError"
            raise RuntimeError(f"Connection error: {str(e)}")
        except Exception as e:
            self.outcome = "apiError"
            raise e
