from urllib.parse import urlparse

from writer.abstract import register_abstract_template
from writer.blocks.base_block import WriterBlock
from writer.ss_types import AbstractTemplate


class WriterWebSearch(WriterBlock):
    @classmethod
    def register(cls, type: str):
        super(WriterWebSearch, cls).register(type)
        register_abstract_template(
            type,
            AbstractTemplate(
                baseType="blueprints_node",
                writer={
                    "name": "Web search",
                    "description": "Search the web for information and return relevant results with source URLs.",
                    "category": "Writer",
                    "featureFlags": ["web_search_block"],
                    "fields": {
                        "query": {
                            "name": "Query",
                            "type": "Text",
                            "control": "Textarea",
                            "desc": "The search query to find information on the web.",
                            "validator": {
                                "type": "string",
                                "minLength": 1,
                            },
                        },
                        "includeDomains": {
                            "name": "Include domains",
                            "type": "Object",
                            "default": "[]",
                            "desc": "List of domains to specifically search within (e.g., ['wikipedia.org', 'docs.python.org']).",
                            "validator": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                        },
                        "excludeDomains": {
                            "name": "Exclude domains",
                            "type": "Object",
                            "default": "[]",
                            "desc": "List of domains to exclude from search results.",
                            "validator": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                            },
                        },
                        "includeRawContent": {
                            "name": "Include raw content",
                            "type": "Boolean",
                            "default": "no",
                            "desc": "Include the raw content of web pages in the response.",
                            "validator": {
                                "type": "boolean",
                            },
                        },
                    },
                    "outs": {
                        "success": {
                            "name": "Success",
                            "description": "If the web search was successful.",
                            "style": "success",
                        },
                        "error": {
                            "name": "Error",
                            "description": "If the function raises an Exception.",
                            "style": "error",
                        },
                    },
                },
            ),
        )

    def _normalize_domains(self, domains):
        """Normalize and validate domain list."""
        if not isinstance(domains, list):
            raise ValueError("Domains must be a list.")
        
        normalized = []
        seen = set()
        
        for domain in domains:
            if not isinstance(domain, str):
                continue
            
            # Normalize: lowercase, strip whitespace
            normalized_domain = domain.lower().strip()
            
            # Skip empty strings
            if not normalized_domain:
                continue
            
            # Extract hostname (drop protocol, path, query, and port; trim leading www.)
            parsed = urlparse(normalized_domain if '://' in normalized_domain else f'http://{normalized_domain}')
            host = parsed.netloc or parsed.path.split('/', 1)[0]
            
            # Skip if we couldn't extract a valid hostname
            if not host:
                continue
                
            host = host.split(':', 1)[0]  # drop port if any
            if host.startswith('www.'):
                host = host[len('www.'):]
            normalized_domain = host.rstrip('.')
            
            # Skip if normalization resulted in empty domain
            if not normalized_domain:
                continue
            
            # Add to list if not duplicate
            if normalized_domain not in seen:
                seen.add(normalized_domain)
                normalized.append(normalized_domain)
        
        return normalized
    
    def run(self):
        try:
            query = self._get_field("query", required=True)
            include_domains = self._get_field("includeDomains", as_json=True, default_field_value="[]")
            exclude_domains = self._get_field("excludeDomains", as_json=True, default_field_value="[]")
            include_raw_content = self._get_field("includeRawContent", False, "no") == "yes"
            
            # Normalize domain lists
            include_domains = self._normalize_domains(include_domains)
            exclude_domains = self._normalize_domains(exclude_domains)
            
            client = self.writer_sdk_client
            
            # Build the request parameters
            params = {
                "query": query,
                "include_raw_content": include_raw_content,
            }
            
            if include_domains:
                params["include_domains"] = include_domains
            
            if exclude_domains:
                params["exclude_domains"] = exclude_domains
            
            response = client.tools.web_search(**params)
            
            # Extract the answer and sources from the response
            result = {
                "answer": response.answer if hasattr(response, 'answer') else "",
                "sources": []
            }
            
            # Process sources if available
            if hasattr(response, 'sources'):
                for source in response.sources:
                    source_data = {
                        "url": source.url if hasattr(source, 'url') else "",
                        "title": source.title if hasattr(source, 'title') else "",
                        "snippet": source.snippet if hasattr(source, 'snippet') else "",
                    }
                    if include_raw_content and hasattr(source, 'raw_content'):
                        source_data["raw_content"] = source.raw_content
                    result["sources"].append(source_data)
            
            self.result = result
            self.outcome = "success"
            
        except BaseException as e:
            self.outcome = "error"
            raise e
