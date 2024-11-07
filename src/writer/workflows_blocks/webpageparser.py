import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, Any, List, Union
from datetime import datetime
from urllib.parse import urlparse, urljoin
import trafilatura
from readability import Document
import hashlib
from playwright.async_api import async_playwright
import pandas as pd

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock

class WebpageParserIntegration(WorkflowBlock):
    def __init__(self):
        super().__init__()
        self.session = None
        
    @classmethod
    def register(cls, type: str):
        super(WebpageParserIntegration, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Webpage Parser Integration",
                "description": "Parse and extract content from webpages",
                "category": "Web Scraping",
                "fields": {
                    "operation": {
                        "name": "Operation",
                        "type": "Text",
                        "options": {
                            "parse_urls": "Parse URLs",
                            "extract_content": "Extract Content",
                            "extract_structured_data": "Extract Structured Data",
                            "batch_process": "Batch Process URLs",
                            "custom_extraction": "Custom Extraction"
                        },
                        "default": "parse_urls"
                    },
                    "urls": {
                        "name": "URLs",
                        "type": "Text",
                        "description": "Single URL or JSON array of URLs",
                        "required": True
                    },
                    "extraction_rules": {
                        "name": "Extraction Rules",
                        "type": "Key-Value",
                        "description": "CSS selectors or XPath rules for extraction",
                        "default": "{}",
                        "required": False
                    },
                    "output_format": {
                        "name": "Output Format",
                        "type": "Text",
                        "options": {
                            "json": "JSON",
                            "csv": "CSV",
                            "text": "Plain Text",
                            "html": "HTML"
                        },
                        "default": "json",
                        "required": False
                    },
                    "include_metadata": {
                        "name": "Include Metadata",
                        "type": "Text",
                        "default": "true",
                        "required": False
                    },
                    "js_rendering": {
                        "name": "JavaScript Rendering",
                        "type": "Text",
                        "default": "false",
                        "required": False
                    },
                    "timeout": {
                        "name": "Timeout",
                        "type": "Text",
                        "default": "30",
                        "required": False
                    }
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The parsing operation completed successfully.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "An error occurred during parsing.",
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

    async def _get_page_content(self, url: str, js_rendering: bool = False, timeout: int = 30) -> str:
        """Fetch webpage content with optional JavaScript rendering"""
        try:
            if js_rendering == "true":
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    await page.goto(url, timeout=timeout * 1000)
                    content = await page.content()
                    await browser.close()
                    return content
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=timeout) as response:
                        return await response.text()
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Error fetching content from {url}: {str(e)}")

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from webpage"""
        metadata = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "title": soup.title.string if soup.title else None,
            "meta_description": None,
            "meta_keywords": None,
            "canonical_url": None,
            "author": None,
            "publication_date": None
        }
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            if meta.get('name') == 'description':
                metadata['meta_description'] = meta.get('content')
            elif meta.get('name') == 'keywords':
                metadata['meta_keywords'] = meta.get('content')
            elif meta.get('name') == 'author':
                metadata['author'] = meta.get('content')
            elif meta.get('property') == 'article:published_time':
                metadata['publication_date'] = meta.get('content')
        
        # Extract canonical URL
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical:
            metadata['canonical_url'] = canonical.get('href')
            
        return metadata

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

    async def _extract_content(self, url: str, html: str) -> Dict[str, Any]:
        """Extract main content from webpage"""
        try:
            # Use trafilatura for main content extraction
            main_content = trafilatura.extract(html, include_comments=False)
            
            # Use readability as backup
            if not main_content:
                doc = Document(html)
                main_content = doc.summary()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract metadata if enabled
            metadata = self._extract_metadata(soup, url)
            
            return {
                "url": url,
                "content": self._clean_text(main_content) if main_content else None,
                "metadata": metadata,
                "html": html
            }
        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Error extracting content from {url}: {str(e)}")

    async def _extract_structured_data(self, html: str, rules: Dict[str, str]) -> Dict[str, Any]:
        """Extract structured data using custom rules"""
        soup = BeautifulSoup(html, 'html.parser')
        structured_data = {}
        
        for field, selector in rules.items():
            try:
                if selector.startswith('//'):  # XPath
                    # Convert to CSS selector for simplicity
                    elements = soup.select(selector)
                else:  # CSS selector
                    elements = soup.select(selector)
                
                extracted = [self._clean_text(el.get_text()) for el in elements]
                structured_data[field] = extracted[0] if len(extracted) == 1 else extracted
            except Exception as e:
                structured_data[field] = None
                
        return structured_data

    def _format_output(self, data: Union[Dict, List], format: str) -> Any:
        """Format extracted data according to specified output format"""
        if format == "json":
            return json.dumps(data, indent=2)
        elif format == "csv":
            df = pd.DataFrame(data if isinstance(data, list) else [data])
            return df.to_csv(index=False)
        elif format == "text":
            if isinstance(data, list):
                return "\n\n".join([item.get('content', '') for item in data])
            return data.get('content', '')
        else:  # html
            return data.get('html', '')

    async def _process_single_url(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single URL with given configuration"""
        js_rendering = config.get('js_rendering', 'false')
        timeout = int(config.get('timeout', 30))
        extraction_rules = json.loads(config.get('extraction_rules', '{}'))
        
        html = await self._get_page_content(url, js_rendering, timeout)
        content = await self._extract_content(url, html)
        
        if extraction_rules:
            structured_data = await self._extract_structured_data(html, extraction_rules)
            content['structured_data'] = structured_data
            
        return content

    async def run(self):
        try:
            # Get configuration
            urls = self._get_field("urls")
            operation = self._get_field("operation")
            output_format = self._get_field("output_format", True, "json")
            include_metadata = self._get_field("include_metadata", True, "true")
            
            # Parse URLs
            if isinstance(urls, str):
                if urls.startswith('['):
                    urls = json.loads(urls)
                else:
                    urls = [urls]

            # Process URLs based on operation
            if operation == "parse_urls":
                results = []
                for url in urls:
                    result = await self._process_single_url(url, self._fields)
                    results.append(result)
                    
            elif operation == "extract_content":
                results = []
                for url in urls:
                    html = await self._get_page_content(url)
                    content = await self._extract_content(url, html)
                    results.append(content)
                    
            elif operation == "extract_structured_data":
                extraction_rules = json.loads(self._get_field("extraction_rules"))
                results = []
                for url in urls:
                    html = await self._get_page_content(url)
                    structured_data = await self._extract_structured_data(html, extraction_rules)
                    results.append({
                        "url": url,
                        "data": structured_data
                    })
                    
            elif operation == "batch_process":
                results = await asyncio.gather(*[
                    self._process_single_url(url, self._fields)
                    for url in urls
                ])
                
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            # Format results
            formatted_output = self._format_output(
                results[0] if len(results) == 1 else results,
                output_format
            )
            
            # Set result
            self.result = {
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "urls_processed": len(urls),
                "output_format": output_format,
                "data": formatted_output
            }
            self.outcome = "success"

        except Exception as e:
            self.outcome = "error"
            raise RuntimeError(f"Error processing URLs: {str(e)}")

