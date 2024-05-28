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

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from writer.ai import Conversation, WriterAIManager, complete, init, stream_complete
from writerai import Writer
from writerai._streaming import Stream
from writerai.types import Chat, ChatStreamingData, Completion, StreamingData


# Decorator to mark tests as explicit, i.e. that they only to be run on direct demand
explicit = pytest.mark.explicit


test_complete_literal = "Completed text"


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
                        "message": {
                            "role": "assistant",
                            "content": "Response"
                            }
                    }
                ],
                created=0,
                model="test"
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
            cast_to=ChatStreamingData,
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
def test_init_writer_ai_manager(emulate_app_process):
    manager = init("fake_token")
    assert isinstance(manager, WriterAIManager)
    assert manager.client.api_key == "fake_token"


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
