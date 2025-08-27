import pytest
from writer.blocks.writerwebsearch import WriterWebSearch


class MockWebSearchResponse:
    def __init__(self):
        self.answer = "Python is a programming language created by Guido van Rossum."
        self.sources = [
            MockSource("https://python.org", "Python Official Site", "Python is a programming language..."),
            MockSource("https://en.wikipedia.org/wiki/Python", "Python - Wikipedia", "Python is an interpreted...")
        ]


class MockSource:
    def __init__(self, url, title, snippet, raw_content=None):
        self.url = url
        self.title = title
        self.snippet = snippet
        self.raw_content = raw_content


class MockClient:
    def __init__(self):
        self.tools = MockTools()


class MockTools:
    def web_search(self, query, include_domains=None, exclude_domains=None, include_raw_content=False):
        # Accept any query for flexibility in tests
        assert isinstance(query, str) and len(query) > 0
        
        response = MockWebSearchResponse()
        
        # Add raw content if requested
        if include_raw_content:
            for source in response.sources:
                source.raw_content = f"Full content of {source.title}"
        
        return response


def test_web_search_basic(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.blocks.writerwebsearch.WriterWebSearch.writer_sdk_client", MockClient())
    
    session.session_state["search_query"] = "What is Python programming language?"
    component = session.add_fake_component({
        "query": "@{search_query}",
        "includeDomains": "[]",
        "excludeDomains": "[]",
        "includeRawContent": "no"
    })
    
    block = WriterWebSearch(component, runner, {})
    block.run()
    
    assert block.outcome == "success"
    assert block.result["answer"] == "Python is a programming language created by Guido van Rossum."
    assert len(block.result["sources"]) == 2
    assert block.result["sources"][0]["url"] == "https://python.org"
    assert block.result["sources"][0]["title"] == "Python Official Site"
    assert "raw_content" not in block.result["sources"][0]


def test_web_search_with_domains(monkeypatch, session, runner, fake_client):
    monkeypatch.setattr("writer.blocks.writerwebsearch.WriterWebSearch.writer_sdk_client", MockClient())
    
    session.session_state["include_sites"] = ["python.org", "docs.python.org"]
    session.session_state["exclude_sites"] = ["spam.com"]
    
    component = session.add_fake_component({
        "query": "Python tutorial",
        "includeDomains": "@{include_sites}",
        "excludeDomains": "@{exclude_sites}",
        "includeRawContent": "yes"
    })
    
    block = WriterWebSearch(component, runner, {})
    block.run()
    
    assert block.outcome == "success"
    assert "raw_content" in block.result["sources"][0]


def test_web_search_missing_query(session, runner, fake_client):
    component = session.add_fake_component({
        "includeDomains": "[]",
        "excludeDomains": "[]"
    })
    
    block = WriterWebSearch(component, runner, {})
    
    with pytest.raises(Exception):  # WriterConfigurationError for missing field
        block.run()


def test_web_search_invalid_domains(session, runner, fake_client):
    component = session.add_fake_component({
        "query": "test query",
        "includeDomains": "not a list",
        "excludeDomains": "[]"
    })
    
    block = WriterWebSearch(component, runner, {})
    
    with pytest.raises(Exception):  # WriterConfigurationError for invalid JSON
        block.run()


def test_normalize_domains():
    """Test domain normalization logic."""
    block = WriterWebSearch.__new__(WriterWebSearch)  # Skip __init__
    
    # Test cases: (input, expected_output)
    test_cases = [
        # Basic domains
        (["example.com"], ["example.com"]),
        (["www.example.com"], ["example.com"]),
        
        # Full URLs with paths/queries
        (["https://example.com/docs/page"], ["example.com"]),
        (["http://api.github.com/repos/user/repo"], ["api.github.com"]),
        
        # URLs with ports
        (["http://example.com:8080/path"], ["example.com"]),
        (["https://www.example.com:443"], ["example.com"]),
        
        # Subdomains
        (["subdomain.example.com/path"], ["subdomain.example.com"]),
        (["www.subdomain.example.com"], ["subdomain.example.com"]),
        
        # Edge cases
        ([""], []),  # Empty string
        (["   "], []),  # Whitespace only
        ([123], []),  # Non-string input
        (["example.com", "example.com"], ["example.com"]),  # Duplicates
        (["EXAMPLE.COM"], ["example.com"]),  # Case normalization
        
        # Invalid domains (should be skipped)
        ([""], []),
        (["://invalid"], []),
        
        # Mixed valid/invalid
        (["example.com", "", "github.com"], ["example.com", "github.com"]),
    ]
    
    for inputs, expected in test_cases:
        result = block._normalize_domains(inputs)
        assert result == expected, f"Input {inputs} -> {result}, expected {expected}"


def test_normalize_domains_invalid_input():
    """Test domain normalization with invalid input types."""
    block = WriterWebSearch.__new__(WriterWebSearch)  # Skip __init__
    
    with pytest.raises(ValueError, match="Domains must be a list"):
        block._normalize_domains("not a list")
    
    with pytest.raises(ValueError, match="Domains must be a list"):
        block._normalize_domains(123)