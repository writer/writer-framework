"""
# AI Module Test Suite

This module provides a suite of tests for the AI integration with the Writer SDK.

## Types of tests

1. **Mock tests**
   - These tests simulate interactions with the Writer AI SDK without making real API calls.
   - They are faster and can be run frequently during development.

2. **SDK query tests**
   - These tests make real API calls to the Writer AI service.
   - They are intended for use on potentially breaking changes and major releases to ensure compatibility with the live API.

## Running the tests

By default, SDK query tests are marked with the custom `explicit` decorator and are excluded from regular test runs.
Only mock tests are run by regular `pytest` command:

```sh
pytest ./tests/backend/test_ai.py
```

To run SDK query tests, ensure you have `pytest-env` installed:
```sh
pip install pytest-env
```

Then, set the `WRITER_API_KEY` environment variable in `pytest.ini` file:
```ini
[pytest]
env =
    WRITER_API_KEY=your_api_key_here
```

After that, to include SDK query tests into the run, use the `--full-run` option:
```sh
pytest ./tests/backend/test_ai.py --full-run
```
"""

import time
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from writer.ai import (
    Conversation,
    File,
    FileDeleteResponse,
    Graph,
    GraphDeleteResponse,
    GraphRemoveFileFromGraphResponse,
    SDKFile,
    SDKGraph,
    WriterAIManager,
    apps,
    ask,
    complete,
    create_function_tool,
    create_graph,
    delete_file,
    delete_graph,
    init,
    list_files,
    list_graphs,
    retrieve_file,
    retrieve_graph,
    stream_ask,
    stream_complete,
    upload_file,
)
from writerai import Writer
from writerai._streaming import Stream
from writerai.types import (
    ApplicationGenerateContentResponse,
    Chat,
    ChatCompletionChunk,
    Completion,
    StreamingData,
)

# Decorator to mark tests as explicit, i.e. that they only to be run on direct demand
explicit = pytest.mark.explicit


test_complete_literal = "Completed text"


@pytest.fixture
def mock_app_content_generation():
    with patch('writer.ai.WriterAIManager.acquire_client') as mock_acquire_client:
        original_client = Writer(api_key="fake_token")
        non_streaming_client = AsyncMock(original_client)
        mock_acquire_client.return_value = non_streaming_client

        non_streaming_client.applications.generate_content.return_value = ApplicationGenerateContentResponse(
            suggestion=test_complete_literal
        )

        yield non_streaming_client


@pytest.fixture
def mock_writer_client():
    """Mock fixture for Writer client with configurable behavior."""
    with patch('writer.ai.WriterAIManager.acquire_client') as mock_acquire_client:
        original_client = Writer(api_key="fake_token")
        mock_client = AsyncMock(original_client)
        mock_acquire_client.return_value = mock_client

        # Attach the original client for use in tests
        mock_client._original_client = original_client

        # Basic response mock
        mock_client.completions.create.return_value = Completion(
            choices=[{"text": "Completed text"}]
        )

        def mock_chat_response(include_tool_calls=None):
            """Configurable mock chat response."""
            tool_calls = include_tool_calls if include_tool_calls else None
            return Chat(
                id="test",
                choices=[
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Response",
                            "tool_calls": tool_calls,
                        },
                    }
                ],
                created=0,
                model="test",
                object="chat.completion"
                )
        mock_client.completions.create.return_value = \
            Completion(choices=[{"text": test_complete_literal}])

        mock_client.graphs.question.return_value = \
            MagicMock(answer="Mocked Answer")

        mock_client.chat.create_chat_response = mock_chat_response

        # Shared fake stream response generator
        def fake_stream_response():
            yield b'data: {"choices":[{"message":{"content":"part1","role":"assistant"}}]}\n\n'
            yield b'data: {"choices":[{"message":{"content":"part2","role":"assistant"}}]}\n\n'

        mock_client.fake_stream_response = fake_stream_response
        yield mock_client


@pytest.fixture
def mock_non_streaming_client(mock_writer_client):
    """Mock client without tool calls."""
    mock_writer_client.chat.chat.return_value = mock_writer_client.chat.create_chat_response()
    yield mock_writer_client


@pytest.fixture
def mock_tool_calls_client(mock_writer_client):
    """Mock client with tool calls returned only once."""
    tool_calls = [
        {"id": "1", "type": "function", "function": {"name": "test_function", "arguments": '{"arg1": 5}'}},
        {"id": "2", "type": "function", "function": {"name": "test_function", "arguments": '{"arg1": 7}'}},
    ]

    tool_calls_control = {
        "check_enabled": True,  # Toggle for enabling/disabling the check
        "returned": False       # Tracks if tool calls have been returned
    }
    def conditional_chat_response(*args, **kwargs):
        # Return tool calls only on the first call
        if tool_calls_control["returned"]:
            return mock_writer_client.chat.create_chat_response()
        else:
            if tool_calls_control["check_enabled"]:
                tool_calls_control["returned"] = True
            return mock_writer_client.chat.create_chat_response(
                include_tool_calls=mock_writer_client.tool_calls
                )

    # Apply the conditional response to the mock
    mock_writer_client.tool_calls = tool_calls
    mock_writer_client.tool_calls_control = tool_calls_control
    mock_writer_client.chat.chat.side_effect = conditional_chat_response
    yield mock_writer_client


@pytest.fixture
def mock_streaming_client(mock_writer_client):
    """Mock client for streaming."""
    mock_stream = Stream(
        client=mock_writer_client._original_client,
        cast_to=Chat,
        response=httpx.Response(200, content=mock_writer_client.fake_stream_response()),
    )
    mock_writer_client.chat.chat.return_value = mock_stream

    mock_completion_stream = MagicMock()
    mock_completion_stream.__iter__.return_value = iter([
        StreamingData(value="part1"),
        StreamingData(value=" part2")
    ])
    mock_writer_client.completions.create.return_value = \
            mock_completion_stream

    # Mock question streaming
    mock_graph_stream = MagicMock()
    mock_graph_stream._iter_events.return_value = iter([
        MagicMock(data='{"answer": "Part 1"}'),
        MagicMock(data='{"answer": "Part 2"}'),
    ])
    mock_writer_client.graphs.question.return_value = mock_graph_stream
    yield mock_writer_client


@pytest.fixture
def mock_streaming_tool_calls_client(mock_writer_client):
    """Mock client with tool calls returned only once."""
    tool_calls_control = {
        "check_enabled": True,  # Toggle for enabling/disabling the check
        "returned": False       # Tracks if tool calls have been returned
    }
    tool_call_stream = [
        b'data: {"id":"a2a302fa-a85c-44b4-9c20-0956d557517c","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":null,"delta":{"content":"","role":"assistant","tool_calls":null,"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
        b'data: {"id":"dc06043b-b002-40d3-b3fb-e6f1c2a090bc","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":null,"delta":{"content":null,"role":"assistant","tool_calls":[{"index":0,"id":"chatcmpl-tool-1ff1df7d81074e5995ec77af2911f7c1","type":"function","function":{"name":"test_function","arguments":null}}],"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
        b'data: {"id":"10d482f0-e370-41f6-9101-846d3ccbd3c6","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":null,"delta":{"content":null,"role":"assistant","tool_calls":[{"index":0,"id":null,"type":null,"function":{"name":null,"arguments":"{\\"arg1\\": 5"}}],"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
        b'data: {"id":"3eaf20c3-5af0-4b6e-a604-e6bd62bd24ee","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":null,"delta":{"content":null,"role":"assistant","tool_calls":[{"index":0,"id":null,"type":null,"function":{"name":null,"arguments":""}}],"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
        b'data: {"id":"433e565b-38e9-4d20-8c27-ffc33b252669","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":null,"delta":{"content":null,"role":"assistant","tool_calls":[{"index":0,"id":null,"type":null,"function":{"name":null,"arguments":"}"}}],"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
        b'data: {"id":"5091cdb6-2bed-4a55-9625-77c5cd607383","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":null,"delta":{"content":"\\n","role":"assistant","tool_calls":null,"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
        b'data: {"id":"b526eb17-0751-4d6b-8c61-332a28efbac3","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":null,"delta":{"content":null,"role":"assistant","tool_calls":[{"index":1,"id":"chatcmpl-tool-22538c865437437e8ace8076a5755749","type":"function","function":{"name":"test_function","arguments":null}}],"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
        b'data: {"id":"6cc43656-4ea1-43cc-8538-212476bc5681","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":null,"delta":{"content":null,"role":"assistant","tool_calls":[{"index":1,"id":null,"type":null,"function":{"name":null,"arguments":"{\\"arg1\\": 7"}}],"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
        b'data: {"id":"a68791cf-f01a-42fd-87bc-d209b2075e13","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":null,"delta":{"content":null,"role":"assistant","tool_calls":[{"index":1,"id":null,"type":null,"function":{"name":null,"arguments":""}}],"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
        b'data: {"id":"168bc578-1916-448b-8373-1c473383c0cb","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":"tool_calls","delta":{"content":null,"role":"assistant","tool_calls":[{"index":1,"id":null,"type":null,"function":{"name":null,"arguments":"}"}}],"graph_data":{"sources":null,"status":null,"subqueries":null},"refusal":null},"logprobs":null}],"created":1731919162,"model":"palmyra-x-004","usage":null,"system_fingerprint":"v1","service_tier":null}\n\n',
    ]
    def fake_stream_with_tool_calls():
        """Generate streaming data with tool calls in JSON format for the first chunk."""
        if tool_calls_control["returned"]:
            # Use the original fake stream response
            yield from mock_writer_client.fake_stream_response()
        else:
            if tool_calls_control["check_enabled"]:
                tool_calls_control["returned"] = True
            for chunk in mock_writer_client.tool_call_stream:
                yield chunk

    # Mock the streaming response with the modified generator
    def create_mock_stream(*args, **kwargs):
        mock_stream = Stream(
            client=mock_writer_client._original_client,
            cast_to=Chat,
            response=httpx.Response(200, content=fake_stream_with_tool_calls()),
        )
        return mock_stream

    mock_writer_client.tool_call_stream = tool_call_stream
    mock_writer_client.tool_calls_control = tool_calls_control
    mock_writer_client.chat.chat.side_effect = create_mock_stream
    yield mock_writer_client


@pytest.fixture
def sdk_graph_mock():
    return SDKGraph(
        id="test_graph_id",
        created_at=datetime.now(),
        file_status={"completed": 0, "failed": 0, "in_progress": 0, "total": 0},
        name="test_graph",
        description="A test graph"
    )


@pytest.fixture
def sdk_file_mock():
    return SDKFile(
        id="test_file_id",
        created_at=datetime.now(),
        graph_ids=["test_graph_id"],
        name="test_file",
        status="test"
    )


@pytest.fixture
def mock_graphs_accessor(sdk_file_mock, sdk_graph_mock):
    with patch('writer.ai.Graph._retrieve_graphs_accessor') as mock_acquire_client:
        mock_accessor = MagicMock()
        mock_graph = Graph(sdk_graph_mock)
        mock_file = File(sdk_file_mock)
        mock_accessor.create.return_value = mock_graph
        mock_accessor.add_file_to_graph.return_value = mock_file
        mock_accessor.retrieve.return_value = mock_graph
        mock_accessor.list.return_value = [mock_graph]
        mock_accessor.delete.return_value = GraphDeleteResponse(id="test_file_id", deleted=True)
        mock_accessor.remove_file_from_graph.return_value = GraphRemoveFileFromGraphResponse(id="test_file_id", deleted=True)

        mock_acquire_client.return_value = mock_accessor
        yield mock_accessor


@pytest.fixture
def mock_files_accessor(sdk_file_mock):
    with patch('writer.ai.File._retrieve_files_accessor') as mock_acquire_client:
        mock_accessor = MagicMock()
        mock_file = File(sdk_file_mock)
        mock_accessor.retrieve.return_value = mock_file
        mock_accessor.list.return_value = [mock_file]
        mock_accessor.upload.return_value = mock_file
        mock_accessor.delete.return_value = FileDeleteResponse(id="test_delete", deleted=True)
        mock_acquire_client.return_value = mock_accessor
        yield mock_accessor


@pytest.fixture
def created_graphs():
    graphs = []
    yield graphs
    for graph in graphs:
        delete_graph(graph_id_or_graph=graph.id)


@pytest.fixture
def created_files():
    files = []
    yield files
    for file in files:
        delete_file(file_id_or_file=file.id)


class FakeAppProcessForAIManager:
    def __init__(self, token):
        self.ai_manager = WriterAIManager(token=token)


def create_fake_app_process(token: str) -> FakeAppProcessForAIManager:
    """
    Helper function to create and patch FakeAppProcessForAIManager with a given token.
    """
    fake_process = FakeAppProcessForAIManager(token)
    method_to_patch = 'writer.ai.WriterAIManager.acquire_instance'
    patcher = patch(method_to_patch, return_value=fake_process.ai_manager)
    patcher.start()
    return fake_process


@pytest.fixture
def emulate_app_process(request):
    token = None
    marker = request.node.get_closest_marker('set_token')
    if marker:
        token = marker.args[0]
    with patch('writer.ai.get_app_process') as mock_get_app_process:
        fake_process = create_fake_app_process(token)
        mock_get_app_process.return_value = fake_process
        yield fake_process
        patch.stopall()


def test_conversation_init_with_prompt():
    # Initialize with a system prompt
    prompt = "You are a social media expert in the financial industry"
    conversation = Conversation(prompt)

    assert len(conversation.messages) == 1
    assert conversation.messages[0] == {
        "role": "system",
        "content": prompt,
        "actions": None
    }


def test_conversation_init_with_history():
    # Initialize with a history of messages
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi, how can I help?"}
    ]
    conversation = Conversation(history)

    assert len(conversation.messages) == len(history)
    for i, message in enumerate(history):
        assert conversation.messages[i] == {**message, "actions": None}


def test_conversation_add_message():
    # Initialize a conversation and add a message
    conversation = Conversation("Initial prompt")

    conversation.add("user", "Hello")

    assert len(conversation.messages) == 2
    assert conversation.messages[1] == {
        "role": "user",
        "content": "Hello",
        "actions": None
    }


def test_conversation_add_chunk_to_last_message():
    # Initialize a conversation and add chunks to the last message
    conversation = Conversation("Initial prompt")

    # Add initial message from the user
    conversation.add("user", "Hello")

    # Add a chunk
    chunk1 = {"content": "How", "chunk": True}
    conversation += chunk1

    # Add another chunk
    chunk2 = {"content": " are you?", "chunk": True}
    conversation += chunk2

    assert len(conversation.messages) == 2
    assert conversation.messages[1] == {
        "role": "user",
        "content": "HelloHow are you?",
        "actions": None
    }


def test_conversation_validate_message():
    # Test message validation
    valid_message = {"role": "user", "content": "Hello"}
    invalid_message_no_role = {"content": "Hello"}
    invalid_message_no_content = {"role": "user"}
    invalid_message_wrong_role = {"role": "unknown", "content": "Hello"}
    invalid_message_non_dict = "Invalid message"

    # This should pass without exceptions
    Conversation.validate_message(valid_message)

    # These should raise ValueError
    with pytest.raises(ValueError):
        Conversation.validate_message(invalid_message_no_role)
    with pytest.raises(ValueError):
        Conversation.validate_message(invalid_message_no_content)
    with pytest.raises(ValueError):
        Conversation.validate_message(invalid_message_wrong_role)
    with pytest.raises(ValueError):
        Conversation.validate_message(invalid_message_non_dict)


def test_conversation_serialized_messages_excludes_system():
    # Initialize with a mix of system and non-system messages
    history = [
        {"role": "system", "content": "System message"},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi, how can I help?"},
        {"role": "system", "content": "Another system message"}
    ]
    conversation = Conversation(history)

    serialized_messages = conversation.serialized_messages

    # Ensure system messages are excluded
    assert len(serialized_messages) == 2
    assert all(message["role"] != "system" for message in serialized_messages)
    assert serialized_messages[0] == \
        {"role": "user", "content": "Hello", "actions": None}
    assert serialized_messages[1] == \
        {"role": "assistant", "content": "Hi, how can I help?", "actions": None}


@pytest.mark.set_token("fake_token")
@pytest.mark.asyncio
def test_conversation_complete(emulate_app_process, mock_non_streaming_client):
    conversation = Conversation()
    response = conversation.complete()

    assert response["role"] == "assistant"
    assert response["content"] == "Response"


@pytest.mark.set_token("fake_token")
def test_conversation_stream_complete(emulate_app_process, mock_streaming_client):
    # Create the Conversation object and collect the response chunks
    conversation = Conversation("Initial prompt")

    response_chunks = []
    for chunk in conversation.stream_complete():
        response_chunks.append(chunk)

    # Verify the content
    assert " ".join(chunk["content"] for chunk in response_chunks) == "part1 part2"


@pytest.mark.set_token("fake_token")
def test_conversation_with_tool_call(emulate_app_process, mock_tool_calls_client):
    def test_function(arg1):
        return int(arg1) ** 2

    conversation = Conversation()
    conversation._register_callable(test_function, "test_function", {"arg1": {"type": "integer"}})

    conversation.add("user", "Call a tool")
    _ = conversation.complete(tools=[{
        "type": "function",
        "callable": test_function,
        "name": "test_function",
        "parameters": {"arg1": {"type": "string"}}
    }])
    tool_results = [message for message in conversation.messages if message["role"] == "tool"]
    assert len(tool_results) == 2
    assert tool_results[0]["content"] == "25"
    assert tool_results[1]["content"] == "49"


@pytest.mark.set_token("fake_token")
def test_conversation_with_stream_tool_call(emulate_app_process, mock_streaming_tool_calls_client):
    def test_function(arg1):
        return int(arg1) ** 2

    conversation = Conversation()
    conversation._register_callable(test_function, "test_function", {"arg1": {"type": "integer"}})

    conversation.add("user", "Call a tool")
    response = conversation.stream_complete(tools=[{
        "type": "function",
        "callable": test_function,
        "name": "test_function",
        "parameters": {"arg1": {"type": "string"}}
    }])
    # Initiate streaming to trigger the calls
    for _ in response:
        pass
    tool_results = [message for message in conversation.messages if message["role"] == "tool"]
    assert len(tool_results) == 2
    assert tool_results[0]["content"] == "25"
    assert tool_results[1]["content"] == "49"


@pytest.mark.set_token("fake_token")
def test_conversation_with_bad_tool_call(emulate_app_process, mock_tool_calls_client):
    def test_function(arg1):
        return int(arg1) ** 2

    # Prepare bad tool call data
    mock_tool_calls_client.tool_calls = [
        {"id": "1", "type": "function", "function": {"name": "test_function", "arguments": '{"arg1": "invalid"}'}},
        {"id": "2", "type": "function", "function": {"name": "test_function", "arguments": '{"arg2": 5}'}},  # Missing 'arg1'
    ]

    conversation = Conversation()
    conversation._register_callable(test_function, "test_function", {"arg1": {"type": "integer"}})

    conversation.add("user", "Call a tool")

    _ = conversation.complete(tools=[{
        "type": "function",
        "callable": test_function,
        "name": "test_function",
        "parameters": {"arg1": {"type": "string"}}
    }])
    tool_results = [message for message in conversation.messages if message["role"] == "tool"]
    assert len(tool_results) == 2
    assert "inform the user about the error" in tool_results[0]["content"]
    assert "inform the user about the error" in tool_results[1]["content"]


@pytest.mark.set_token("fake_token")
def test_conversation_with_stream_bad_tool_call(emulate_app_process, mock_streaming_tool_calls_client):
    def test_function(arg1):
        return int(arg1) ** 2

    # Prepare bad tool call data
    mock_streaming_tool_calls_client.tool_call_stream = [
        b'data: {"id":"1","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":null,"role":"assistant","tool_calls":[{"index":0,"id":"1","type":"function","function":{"name":"test_function","arguments":"{\\"arg1\\":\\"invalid\\"}"}}]}}]}\n\n',
        b'data: {"id":"2","object":"chat.completion.chunk","choices":[{"index":0,"finish_reason":"tool_calls","delta":{"content":null,"role":"assistant","tool_calls":[{"index":1,"id":"2","type":"function","function":{"name":"test_function","arguments":"{\\"arg2\\": 5}"}}]}}]}\n\n',  # Missing 'arg1'
    ]

    conversation = Conversation()
    conversation._register_callable(test_function, "test_function", {"arg1": {"type": "integer"}})

    conversation.add("user", "Call a tool")

    response = conversation.stream_complete(tools=[{
        "type": "function",
        "callable": test_function,
        "name": "test_function",
        "parameters": {"arg1": {"type": "string"}}
    }])
    # Initiate streaming to trigger the calls
    for _ in response:
        pass
    tool_results = [message for message in conversation.messages if message["role"] == "tool"]
    assert len(tool_results) == 2
    assert "inform the user about the error" in tool_results[0]["content"]
    assert "inform the user about the error" in tool_results[1]["content"]

@pytest.mark.set_token("fake_token")
def test_conversation_with_tool_call_max_depth(emulate_app_process, mock_tool_calls_client):
    def test_function(arg1):
        return int(arg1) ** 2
    mock_tool_calls_client.tool_calls_control["check_enabled"] = False
    conversation = Conversation()
    conversation._register_callable(test_function, "test_function", {"arg1": {"type": "integer"}})

    conversation.add("user", "Call a tool")
    with pytest.raises(RuntimeError):
        _ = conversation.complete(tools=[{
            "type": "function",
            "callable": test_function,
            "name": "test_function",
            "parameters": {"arg1": {"type": "string"}}
        }])


@pytest.mark.set_token("fake_token")
def test_conversation_with_stream_tool_call_max_depth(emulate_app_process, mock_streaming_tool_calls_client):
    def test_function(arg1):
        return int(arg1) ** 2
    mock_streaming_tool_calls_client.tool_calls_control["check_enabled"] = False
    conversation = Conversation()
    conversation._register_callable(test_function, "test_function", {"arg1": {"type": "integer"}})

    conversation.add("user", "Call a tool")
    with pytest.raises(RuntimeError):
        response = conversation.stream_complete(tools=[{
            "type": "function",
            "callable": test_function,
            "name": "test_function",
            "parameters": {"arg1": {"type": "string"}}
        }])
        # Initiate streaming to trigger the calls
        for _ in response:
            pass

@pytest.mark.set_token("fake_token")
def test_complete(emulate_app_process, mock_non_streaming_client):
    response = complete("test")

    assert response == test_complete_literal


@pytest.mark.set_token("fake_token")
def test_stream_complete(emulate_app_process, mock_streaming_client):
    response_chunks = list(stream_complete("test"))

    assert "".join(response_chunks) == "part1 part2"


@pytest.mark.set_token("fake_token")
def test_generate_content_from_app(emulate_app_process, mock_app_content_generation):
    response = apps.generate_content("abc123", {
        "Favorite animal": "Dog",
        "Favorite color": "Purple"
    })

    assert response == test_complete_literal


@pytest.mark.set_token("fake_token")
def test_init_writer_ai_manager(emulate_app_process):
    manager = init("fake_token")
    assert isinstance(manager, WriterAIManager)
    assert manager.client.api_key == "fake_token"


def test_create_graph(mock_graphs_accessor):
    graph = create_graph(name="test_graph", description="A test graph")

    # As we modified SDK response, we expect this function
    # to retrieve mock we prepared earlier
    assert graph.id == "test_graph_id"
    assert graph.name == "test_graph"


def test_retrieve_graph(mock_graphs_accessor):
    graph = retrieve_graph(graph_id="test_id")

    # As we modified SDK response, we expect this function
    # to retrieve mock we prepared earlier
    assert graph.id == "test_graph_id"
    assert graph.name == "test_graph"


def test_list_graphs(mock_graphs_accessor):
    graphs = list_graphs()

    # As we modified SDK response, we expect this function
    # to retrieve mock we prepared earlier
    assert len(graphs) == 1
    assert graphs[0].id == "test_graph_id"
    assert graphs[0].name == "test_graph"


def test_delete_graph(mock_graphs_accessor):
    response = delete_graph(graph_id_or_graph="test_graph_id")

    # As we modified SDK response, we expect this function
    # to retrieve mock we prepared earlier
    assert response.deleted is True


def test_add_file_to_graph(mock_graphs_accessor, mock_files_accessor):
    file = retrieve_file(file_id="test_file_id")
    graph = retrieve_graph(graph_id="test_graph_id")
    added_file = graph.add_file(file_id_or_file=file)

    # As we modified SDK response, we expect this function
    # to retrieve mock we prepared earlier
    assert added_file.id == "test_file_id"
    assert added_file.name == "test_file"
    # Graph update should also trigger addition of its ID to stale_ids set
    assert "test_graph_id" in Graph.stale_ids


def test_retrieve_file(mock_files_accessor):
    file = retrieve_file(file_id="test_file_id")

    # As we modified SDK response, we expect this function
    # to retrieve mock we prepared earlier
    assert file.id == "test_file_id"
    assert file.name == "test_file"


def test_list_files(mock_files_accessor):
    files = list_files()

    # As we modified SDK response, we expect this function
    # to retrieve mock we prepared earlier
    assert len(files) == 1
    assert files[0].id == "test_file_id"
    assert files[0].name == "test_file"


def test_upload_file(mock_files_accessor):
    data = b"file_content"
    file = upload_file(data=data, type="text/plain", name="uploaded_file")

    # As we modified SDK response, we expect this function
    # to retrieve mock we prepared earlier
    assert file.id == "test_file_id"
    assert file.name == "test_file"


def test_delete_file(mock_files_accessor):
    response = delete_file(file_id_or_file="test_file_id")

    # As we modified SDK response, we expect this function
    # to retrieve mock we prepared earlier
    assert response.deleted is True


@pytest.mark.set_token("fake_token")
def test_ask(mock_non_streaming_client):
    question = "What is the capital of France?"
    graphs_or_graph_ids = ["graph_id_1"]

    response = ask(question, graphs_or_graph_ids)

    # Assert response and ensure proper method calls
    assert response == "Mocked Answer"
    mock_non_streaming_client.graphs.question.assert_called_once_with(
        graph_ids=["graph_id_1"],
        question=question,
        stream=False,
        subqueries=False
    )


@pytest.mark.set_token("fake_token")
def test_stream_ask(mock_streaming_client):
    question = "Test question"
    graphs_or_graph_ids = ["graph_id_1"]

    response_chunks = list(stream_ask(question, graphs_or_graph_ids))

    # Assert response and ensure proper method calls
    assert response_chunks == ["Part 1", "Part 2"]
    mock_streaming_client.graphs.question.assert_called_once_with(
        graph_ids=["graph_id_1"],
        question=question,
        stream=True,
        subqueries=False
    )


@pytest.mark.set_token("fake_token")
def test_ask_graph_class(mock_non_streaming_client):
    question = "Test question"
    graph_object = Graph(MagicMock(id="test_graph_id"))

    response = graph_object.ask(question)

    # Assert response and ensure proper method calls
    assert response == "Mocked Answer"
    mock_non_streaming_client.graphs.question.assert_called_once_with(
        graph_ids=["test_graph_id"],
        question=question,
        stream=False,
        subqueries=False
    )


@pytest.mark.set_token("fake_token")
def test_stream_ask_graph_class(mock_streaming_client):
    question = "Test question"
    graph_object = Graph(MagicMock(id="test_graph_id"))

    response_chunks = list(graph_object.stream_ask(question))

    # Assert response and ensure proper method calls
    assert response_chunks == ["Part 1", "Part 2"]
    mock_streaming_client.graphs.question.assert_called_once_with(
        graph_ids=["test_graph_id"],
        question=question,
        stream=True,
        subqueries=False
    )


@explicit
def test_explicit_conversation_complete(emulate_app_process):
    conversation = Conversation()
    conversation.add("user", "Hello, how can I improve my social media engagement?")

    response = conversation.complete()

    assert response["role"] == "assistant"
    assert "engagement" in response["content"].lower()


@explicit
def test_explicit_conversation_stream_complete(emulate_app_process):
    conversation = Conversation()
    conversation.add("user", "Hello, how can I improve my social media engagement?")

    response_chunks = []
    for chunk in conversation.stream_complete():
        response_chunks.append(chunk)

    full_response = " ".join(chunk["content"] for chunk in response_chunks)
    assert "engagement" in full_response.lower()


@explicit
def test_explicit_conversation_complete_tool_calls(emulate_app_process):
    secret_word_one = "PARIS"
    correct_password = "Sunshine"
    secret_word_two = "Moonglow"
    number = 15
    coefficient = 2.7

    def test_function_one():
        return secret_word_one

    def test_function_two(password):
        if password == correct_password:
            return secret_word_two

    def test_function_three(number: int, coefficient: float):
        return number * coefficient

    conversation = Conversation()
    conversation.add(
        "user",
        "Use the function to retrieve the secret word. " +
        "Name only the secret word and nothing else."
        )

    # Test a function with no parameters
    first_response = conversation.complete(
        tools=create_function_tool(
            callable=test_function_one,
            name="get_secret_word",
            parameters=None,
            description="A function to retrieve the secret word."
        )
    )

    assert first_response["role"] == "assistant"
    assert first_response["content"] == secret_word_one

    conversation = Conversation()
    conversation.add(
        "user",
        "Use the function to retrieve the secret word. " +
        "Name only the secret word and nothing else. " +
        f"The password is {correct_password}"
        )
    # Test a function with a single parameter
    second_response = conversation.complete(
        tools=create_function_tool(
            callable=test_function_two,
            name="get_secret_word_by_password",
            parameters={
                "password": {
                    "required": True,
                    "type": "string",
                    "description": "A password used to retrieve the secret word"
                    }
                }
        )
    )

    assert second_response["role"] == "assistant"
    assert second_response["content"] == secret_word_two

    conversation = Conversation()
    conversation.add(
        "user",
        "Use the function to calculate the final number. " +
        "Respond with only the resulting calculation and nothing else. " +
        f"The number is {number}. The coefficient is {coefficient}."
        )

    # Test a function with two non-string parameters
    third_response = conversation.complete(
        tools=create_function_tool(
            callable=test_function_three,
            name="calculate",
            parameters={
                "number": {
                    "required": True,
                    "type": "integer",
                    "description": "The base number to perform calculation against",
                },
                "coefficient": {
                    "required": True,
                    "type": "float",
                    "description": "The coefficient to use against the number"
                }
            }
        )
    )

    assert third_response["role"] == "assistant"
    assert third_response["content"] == str(number * coefficient)


@explicit
def test_explicit_conversation_stream_complete_tool_calls(emulate_app_process):
    secret_word_one = "PARIS"
    correct_password = "Sunshine"
    secret_word_two = "Moonglow"
    number = 15
    coefficient = 2.7

    def test_function_one():
        return secret_word_one

    def test_function_two(password):
        if password == correct_password:
            return secret_word_two

    def test_function_three(number: int, coefficient: float):
        return number * coefficient

    conversation = Conversation()
    conversation.add(
        "user",
        "Use the function to retrieve the secret word. " +
        "Name only the secret word and nothing else."
        )

    # Test a function with no parameters
    first_response_stream = conversation.stream_complete(
        tools=create_function_tool(
            callable=test_function_one,
            name="get_secret_word",
            parameters=None,
            description="A function to retrieve the secret word."
        )
    )
    first_response = ""
    for chunk in first_response_stream:
        first_response += chunk.get("content")

    assert first_response == secret_word_one

    conversation = Conversation()
    conversation.add(
        "user",
        "Use the function to retrieve the secret word. " +
        "Name only the secret word and nothing else. " +
        f"The password is {correct_password}"
        )
    # Test a function with a single parameter
    second_response_stream = conversation.stream_complete(
        tools=create_function_tool(
            callable=test_function_two,
            name="get_secret_word_by_password",
            parameters={
                "password": {
                    "required": True,
                    "type": "string",
                    "description": "A password used to retrieve the secret word"
                    }
                }
        )
    )
    second_response = ""
    for chunk in second_response_stream:
        second_response += chunk.get("content")

    assert second_response == secret_word_two

    conversation = Conversation()
    conversation.add(
        "user",
        "Use the function to calculate the final number. " +
        "Respond with only the resulting calculation and nothing else. " +
        f"The number is {number}. The coefficient is {coefficient}."
        )

    # Test a function with two non-string parameters
    third_response_stream = conversation.stream_complete(
        tools=create_function_tool(
            callable=test_function_three,
            name="calculate",
            parameters={
                "number": {
                    "required": True,
                    "type": "integer",
                    "description": "The base number to perform calculation against"
                },
                "coefficient": {
                    "required": True,
                    "type": "float",
                    "description": "The coefficient to use against the number"
                }
            }
        )
    )
    third_response = ""
    for chunk in third_response_stream:
        third_response += chunk.get("content")

    assert third_response == str(number * coefficient)


@explicit
@pytest.mark.asyncio
async def test_explicit_complete(emulate_app_process):
    initial_text = "Write a short paragraph about the benefits of regular exercise."
    response = complete(initial_text)

    assert isinstance(response, str)
    assert len(response) > 0
    assert "exercise" in response.lower()


@explicit
@pytest.mark.asyncio
async def test_explicit_stream_complete(emulate_app_process):
    initial_text = "Write a short paragraph about the benefits of regular exercise."

    response_chunks = list(stream_complete(initial_text))

    full_response = "".join(response_chunks)
    assert isinstance(full_response, str)
    assert len(full_response) > 0
    assert "exercise" in full_response.lower()


@explicit
def test_explicit_create_graph(emulate_app_process, created_graphs):
    graph = create_graph(name="integration_test_graph", description="Integration test graph")
    created_graphs.append(graph)
    assert graph.id is not None
    assert graph.name == "integration_test_graph"


@explicit
def test_explicit_retrieve_graph(emulate_app_process, created_graphs):
    created_graph = create_graph(name="integration_test_graph", description="Integration test graph")
    created_graphs.append(created_graph)
    graph = retrieve_graph(graph_id=created_graph.id)

    assert graph.id == created_graph.id
    assert graph.name == created_graph.name


@explicit
def test_explicit_list_graphs(emulate_app_process, created_graphs):
    # Create a graph to ensure there's at least one graph in the list
    graph = create_graph(name="integration_test_graph", description="Integration test graph")
    created_graphs.append(graph)

    graphs = list_graphs()

    assert len(graphs) > 0
    assert any(g.id == graph.id for g in graphs)


@explicit
def test_explicit_delete_graph(emulate_app_process, created_graphs):
    created_graph = create_graph(name="integration_test_graph", description="Integration test graph")
    created_graphs.append(created_graph)
    response = delete_graph(graph_id_or_graph=created_graph.id)

    # Ensure the graph is removed from created_graphs
    created_graphs.remove(created_graph)

    assert response.deleted is True


@explicit
def test_explicit_upload_file(emulate_app_process, created_files):
    data = b"file_content"
    file = upload_file(data=data, type="text/plain", name="integration_uploaded_file")
    created_files.append(file)

    assert file.id is not None
    assert file.name == "integration_uploaded_file.txt"


@explicit
def test_explicit_retrieve_file(emulate_app_process, created_files):
    uploaded_file = upload_file(data=b"file_content", type="text/plain", name="integration_uploaded_file")
    created_files.append(uploaded_file)
    file = retrieve_file(file_id=uploaded_file.id)

    assert file.id == uploaded_file.id
    assert file.name == uploaded_file.name


@explicit
def test_explicit_list_files(emulate_app_process, created_files):
    # Upload a file to ensure there's at least one file in the list
    data = b"file_content"
    file = upload_file(data=data, type="text/plain", name="integration_uploaded_file")
    created_files.append(file)

    files = list_files()

    assert len(files) > 0
    assert any(f.id == file.id for f in files)


@explicit
def test_explicit_delete_file(emulate_app_process, created_files):
    uploaded_file = upload_file(data=b"file_content", type="text/plain", name="integration_uploaded_file")
    created_files.append(uploaded_file)
    response = delete_file(file_id_or_file=uploaded_file.id)

    # Ensure the file is removed from created_files
    created_files.remove(uploaded_file)

    assert response.deleted is True


@explicit
def test_explicit_ask_graph_class(
    emulate_app_process,
    created_graphs,
    created_files
):
    uploaded_file = upload_file(
        data=b"Source word is PARIS",
        type="text/plain",
        name="code_words"
        )
    created_files.append(uploaded_file)
    graph = create_graph(
        name="integration_test_graph",
        description="Integration test graph"
        )
    created_graphs.append(graph)
    graph.add_file(uploaded_file)

    # Await file processing
    while True:
        try:
            file_status = graph.file_status
        except AttributeError:
            continue

        if file_status.in_progress == 1:
            # File still being processed
            time.sleep(5)
            continue
        else:
            # File is ready
            break

    answer = graph.ask(
        "What is the source word? Name only the word and nothing else"
        )

    assert isinstance(answer, str)
    assert answer == "PARIS"


@explicit
def test_explicit_stream_ask_graph_class(
    emulate_app_process,
    created_graphs,
    created_files
):
    uploaded_file = upload_file(
        data=b"Source word is PARIS",
        type="text/plain",
        name="code_words"
        )
    created_files.append(uploaded_file)
    graph = create_graph(
        name="integration_test_graph",
        description="Integration test graph"
        )
    created_graphs.append(graph)
    graph.add_file(uploaded_file)

    # Await file processing
    while True:
        try:
            file_status = graph.file_status
        except AttributeError:
            continue

        if file_status.in_progress == 1:
            # File still being processed
            time.sleep(5)
            continue
        else:
            # File is ready
            break

    answer = ""
    stream = graph.stream_ask(
        "What is the source word? Name only the word and nothing else"
        )
    for chunk in stream:
        answer += chunk

    assert isinstance(answer, str)
    assert answer == " PARIS"


@explicit
def test_explicit_ask(
    emulate_app_process,
    created_graphs,
    created_files
):
    uploaded_file = upload_file(
        data=b"Source word is PARIS",
        type="text/plain",
        name="code_words"
        )
    created_files.append(uploaded_file)
    graph = create_graph(
        name="integration_test_graph",
        description="Integration test graph"
        )
    created_graphs.append(graph)
    graph.add_file(uploaded_file)

    # Await file processing
    while True:
        try:
            file_status = graph.file_status
        except AttributeError:
            continue

        if file_status.in_progress == 1:
            # File still being processed
            time.sleep(5)
            continue
        else:
            # File is ready
            break

    answer = ask(
        question="What is the source word? Name only the word and nothing else",
        graphs_or_graph_ids=[graph]
        )

    assert isinstance(answer, str)
    assert answer == "PARIS"


@explicit
def test_explicit_stream_ask(
    emulate_app_process,
    created_graphs,
    created_files
):
    uploaded_file = upload_file(
        data=b"Source word is PARIS",
        type="text/plain",
        name="code_words"
        )
    created_files.append(uploaded_file)
    graph = create_graph(
        name="integration_test_graph",
        description="Integration test graph"
        )
    created_graphs.append(graph)
    graph.add_file(uploaded_file)

    # Await file processing
    while True:
        try:
            file_status = graph.file_status
        except AttributeError:
            continue

        if file_status.in_progress == 1:
            # File still being processed
            time.sleep(5)
            continue
        else:
            # File is ready
            break

    answer = ""
    stream = stream_ask(
        question="What is the source word? Name only the word and nothing else",
        graphs_or_graph_ids=[graph]
        )
    for chunk in stream:
        answer += chunk

    assert isinstance(answer, str)
    assert answer == " PARIS"

# For doing a explicit test of apps.generate_content() we need a no-code app that
# nobody will touch. That is a challenge.
