import requests
from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class BraveSearch(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(BraveSearch, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Brave Search",
                "description": "Executes a search query using the Brave Search API.",
                "category": "Search",
                "fields": {
                    "api_key": {
                        "name": "API Key",
                        "type": "Text",
                        "description": "Your Brave Search API key"
                    },
                    "query": {
                        "name": "Search Query",
                        "type": "Text",
                        "description": "The search term or phrase"
                    },
                    "location": {
                        "name": "Location",
                        "type": "Text",
                        "description": "Geographic location for search results",
                        "required": False
                    },
                    "device": {
                        "name": "Device",
                        "type": "Text",
                        "options": {
                            "desktop": "Desktop",
                            "mobile": "Mobile"
                        },
                        "default": "desktop",
                        "required": False
                    },
                    "language": {
                        "name": "Language",
                        "type": "Text",
                        "description": "Language for search results",
                        "default": "en",
                        "required": False
                    },
                    "num_results": {
                        "name": "Number of Results",
                        "type": "Text",
                        "default": "10",
                        "required": False
                    },
                    "additional_params": {
                        "name": "Additional Parameters",
                        "type": "Key-Value",
                        "default": "{}",
                        "required": False
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The search was completed successfully.",
                        "style": "success",
                    },
                    "apiError": {
                        "name": "API Error",
                        "description": "An error occurred while making the API request.",
                        "style": "error",
                    },
                    "rateLimitError": {
                        "name": "Rate Limit Error",
                        "description": "The API rate limit has been exceeded.",
                        "style": "error",
                    }
                },
            }
        ))

    def run(self):
        try:
            # Get required fields
            api_key = self._get_field("api_key")
            query = self._get_field("query")
            
            # Get optional fields
            location = self._get_field("location", True)
            device = self._get_field("device", True, "desktop")
            language = self._get_field("language", True, "en")
            num_results = self._get_field("num_results", True, "10")
            additional_params = self._get_field("additional_params", True, "{}")

            # Construct the API endpoint URL
            url = "https://api.brave.com/v1/search"

            # Prepare parameters
            params = {
                "q": query,
                "location": location,
                "device": device,
                "lang": language,
                "num": num_results
            }

            # Merge additional parameters
            params.update(eval(additional_params))

            # Set the API key in the headers
            headers = {
                "X-Api-Key": api_key
            }

            # Make the API request
            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 429:
                self.outcome = "rateLimitError"
            elif not response.ok:
                self.outcome = "apiError"
            else:
                self.outcome = "success"
                self.result = {
                    "search_metadata": {
                        "status": response.status_code,
                        "created_at": response.headers.get("Date"),
                        "search_engine": "brave"
                    },
                    "search_parameters": params,
                    "search_results": response.json()
                }

        except requests.exceptions.RequestException as e:
            self.outcome = "apiError"
        except Exception as e:
            self.outcome = "apiError"
