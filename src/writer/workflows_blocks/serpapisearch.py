import requests
from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class SerpApiSearch(WorkflowBlock):
    @classmethod
    def register(cls, type: str):
        super(SerpApiSearch, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "SerpApi Search",
                "description": "Executes a search query using SerpApi.",
                "category": "Other",
                "fields": {
                    "api_key": {
                        "name": "API Key",
                        "type": "Text",
                        "description": "Your SerpApi API key"
                    },
                    "search_engine": {
                        "name": "Search Engine",
                        "type": "Text",
                        "options": {
                            "google": "Google",
                            "bing": "Bing",
                            "yahoo": "Yahoo",
                            "yandex": "Yandex"
                        },
                        "default": "google"
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
                    },
                    "num_results": {
                        "name": "Number of Results",
                        "type": "Number",
                        "default": "10",
                    },
                    "additional_params": {
                        "name": "Additional Parameters",
                        "type": "Key-Value",
                        "default": "{}",
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
            search_engine = self._get_field("search_engine", False, "google")
            query = self._get_field("query")
            
            # Get optional fields
            location = self._get_field("location", True)
            num_results = self._get_field("num_results", True, "10")
            additional_params = self._get_field("additional_params", True, "{}")

            # Construct base URL based on search engine
            base_urls = {
                "google": "https://serpapi.com/search.json",
                "bing": "https://serpapi.com/bing/search",
                "yahoo": "https://serpapi.com/yahoo/search",
                "yandex": "https://serpapi.com/yandex/search"
            }

            # Prepare parameters
            params = {
                "api_key": api_key,
                "q": query,
                "num": num_results
            }

            # Add optional parameters
            if location:
                params["location"] = location

            # Merge additional parameters
            params.update(additional_params)

            # Make the API request
            response = requests.get(base_urls[search_engine], params=params)

            if response.status_code == 429:
                self.result = "SerpApi rate limit exceeded"
                self.outcome = "rateLimitError"
                return

            if not response.ok:
                self.result = f"SerpApi error: {response.status_code} - {response.text}"
                self.outcome = "apiError"
                return

            # Parse and store results
            self.result = {
                "search_metadata": {
                    "status": response.status_code,
                    "created_at": response.headers.get("Date"),
                    "search_engine": search_engine
                },
                "search_parameters": params,
                "search_results": response.json()
            }
            
            self.outcome = "success"
        except requests.exceptions.RequestException as e:
            self.outcome = "apiError"
            raise RuntimeError(f"Connection error: {str(e)}")
        except Exception as e:
            self.outcome = "apiError"
            raise e

