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
    complete,
    create_graph,
    delete_file,
    delete_graph,
    init,
    list_files,
    list_graphs,
    retrieve_file,
    retrieve_graph,
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
def mock_non_streaming_client():
    with patch('writer.ai.WriterAIManager.acquire_client') as mock_acquire_client:
        original_client = Writer(api_key="fake_token")
        non_streaming_client = AsyncMock(original_client)
        mock_acquire_client.return_value = non_streaming_client

        non_streaming_client.chat.chat.return_value = \
            Chat(
                id="test",
                choices=[
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "logprobs": {},
                        "message": {
                            "role": "assistant",
                            "content": "Response",
                            "refusal": "false"
                            }
                    },

                ],
                created=0,
                model="test",
                object="chat.completion"
                )
        non_streaming_client.completions.create.return_value = \
            Completion(choices=[{"text": test_complete_literal}])

        yield non_streaming_client


@pytest.fixture
def mock_streaming_client():
    def fake_response_content():
        yield b'data: {"id":"test","choices":[{"finish_reason":"stop","message":{"content":"part1","role":"assistant"}}],"created":0,"model":"test"}\n\n'
        yield b'data: {"id":"test","choices":[{"finish_reason":"stop","message":{"content":"part2","role":"assistant"}}],"created":0,"model":"test"}\n\n'
        yield b'\n'
    with patch('writer.ai.WriterAIManager.acquire_client') as mock_acquire_client:
        original_client = Writer(api_key="fake_token")
        streaming_client = AsyncMock(original_client)
        mock_acquire_client.return_value = streaming_client

        mock_chat_stream = Stream(
            client=original_client,
            cast_to=ChatCompletionChunk,
            response=httpx.Response(
                status_code=200,
                content=fake_response_content()
            )
        )
        streaming_client.chat.chat.return_value = mock_chat_stream

        # Mock completion streaming
        mock_completion_stream = MagicMock()
        mock_completion_stream.__iter__.return_value = iter([
            StreamingData(value="part1"),
            StreamingData(value=" part2")
        ])
        streaming_client.completions.create.return_value = mock_completion_stream

        yield streaming_client


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

# For doing a explicit test of apps.generate_content() we need a no-code app that
# nobody will touch. That is a challenge.
