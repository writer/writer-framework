import logging
from typing import Generator, Iterable, List, Optional, TypedDict, Union, cast

from httpx import Timeout
from writerai import WriterAI
from writerai._streaming import Stream
from writerai._types import Body, Headers, NotGiven, Query
from writerai.types import Chat, Completion, StreamingData
from writerai.types.chat_chat_params import Message

from streamsync.core import get_app_process


class ChatOptions(TypedDict, total=False):
    max_tokens: Union[int, NotGiven]
    n: Union[int, NotGiven]
    stop: Union[List[str], str, NotGiven]
    temperature: Union[float, NotGiven]
    top_p: Union[float, NotGiven]
    extra_headers: Optional[Headers]
    extra_query: Optional[Query]
    extra_body: Optional[Body]
    timeout: Union[float, Timeout, None, NotGiven]


class CreateOptions(TypedDict, total=False):
    best_of: Union[int, NotGiven]
    max_tokens: Union[int, NotGiven]
    random_seed: Union[int, NotGiven]
    stop: Union[List[str], str, NotGiven]
    temperature: Union[float, NotGiven]
    top_p: Union[float, NotGiven]
    extra_headers: Optional[Headers]
    extra_query: Optional[Query]
    extra_body: Optional[Body]
    timeout: Union[float, Timeout, None, NotGiven]


logger = logging.Logger(__name__)


def _process_completion_data_chunk(choice: StreamingData) -> str:
    text = choice.value
    if text:
        return text
    raise ValueError("Failed to retrieve text from completion stream")


def _process_chat_data_chunk(chat_data: Chat) -> dict:
    choices = chat_data.choices
    for entry in choices:
        message = cast(dict, entry.message)
        return message
    raise ValueError("Failed to retrieve text from chat stream")


class WriterAIManager:
    """
    Manages authentication for Writer AI functionalities.

    :ivar token: Authentication token for the Writer AI API.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initializes a WriterAIManager instance.

        This method sets the API URL, authentication token, global temperature setting,
        and global maximum token limit for responses, using environment variables.

        :param token: Optional; the default token for API authentication used if WRITERAI_API_KEY environment variable is not set up.
        """

        self.client = WriterAI(
            # This is the default and can be omitted
            api_key=token,
        )

        current_process = get_app_process()
        setattr(current_process, 'ai_manager', self)

    @classmethod
    def acquire_instance(cls) -> 'WriterAIManager':
        """
        Retrieve the existing instance of WriterAIManager from the current app process.

        :returns: The current instance of the manager.
        :raises RuntimeWarning: If no instance of WriterAIManager is found in the current process.
        """
        current_process = get_app_process()
        try:
            instance = getattr(current_process, 'ai_manager')
            return instance
        except AttributeError:
            raise RuntimeWarning('No WriterAIManager instance found. Have you initialized it?')

    @classmethod
    def authorize(cls, token: str):
        """
        Authorize the WriterAIManager with a new token.
        This can be done as an alternative to setting up an environment variable, or to override the token that was already provided before.

        :param token: The new token to use for authentication.
        """
        instance = cls.acquire_instance()
        instance.client = WriterAI(api_key=token)

    @classmethod
    def use_chat_model(cls) -> str:
        """
        Get the configuration for the chat model.

        :returns: Name for the chat model.
        """
        return "palmyra-chat-v2-32k"

    @classmethod
    def use_completion_model(cls) -> str:
        """
        Get the configuration for the completion model.

        :returns: Name for the completion model.
        """
        return "palmyra-x-v2"

    @classmethod
    def acquire_client(cls) -> WriterAI:
        instance = cls.acquire_instance()
        return instance.client


class Conversation:
    class Message(TypedDict):
        role: str
        content: str
        actions: Optional[dict]

    def __init__(self, config: Optional[dict] = None):
        """
        Initializes the Conversation object.

        :param config: Optional dictionary containing initial configuration settings.
        """
        self.messages: List[Conversation.Message] = []
        self.config = config or {}

    def _merge_chunk_to_last_message(self, raw_chunk: dict):
        """
        Merge a chunk of data into the last message in the conversation.

        This method takes a chunk of data and integrates it into the content of the
        last message of the conversation. It appends additional content if present,
        and merges other key-value pairs into the last message's dictionary.

        :param raw_chunk: A dictionary containing the chunk of data to be merged.
        :raises ValueError: If the Conversation's `messages` list is empty, indicating there is no message to merge the chunk with.
        """
        def _clear_chunk_flag(chunk):
            return {key: value for key, value in chunk.items() if key != "chunk"}
        if not self.messages:
            raise ValueError("No message to merge chunk with")
        clear_chunk = _clear_chunk_flag(raw_chunk)
        updated_last_message: 'Conversation.Message' = self.messages[-1]
        if "content" in clear_chunk:
            updated_last_message["content"] += clear_chunk.pop("content")
        updated_last_message |= clear_chunk

    def __add__(self, chunk_or_message: Union['Message', dict]):
        """
        Adds a message or appends a chunk to the last message in the conversation.

        :param chunk_or_message: Dictionary representation of a message or chunk to add.
        :raises TypeError: If passed chunk_or_message is not a dictionary.
        :raises ValueError: If chunk_or_message is not a proper message with "role" and "content".
        """
        if not isinstance(chunk_or_message, dict):
            raise TypeError("Conversation only supports dict operands for addition")
        if chunk_or_message.get("chunk") is True:
            chunk = chunk_or_message
            self._merge_chunk_to_last_message(cast(dict, chunk))
        else:
            message = chunk_or_message
            if not ("role" in message and "content" in message):
                raise ValueError("Improper message format to add to Conversation")
            self.messages.append({"role": message["role"], "content": message["content"], "actions": message.get("actions")})
        return self

    def add(self, role: str, message: str):
        """
        Adds a new message to the conversation.

        :param role: The role of the message sender.
        :param message: The content of the message.
        """
        self.__add__({"role": role, "content": message})

    def complete(self, data: Optional['ChatOptions'] = None) -> str:
        """
        Processes the conversation with the current messages and additional data to generate a response.

        :param data: Optional parameters to pass for processing.
        :return: The content of the generated response.
        :raises RuntimeError: If response data was not properly formatted to retrieve model text.
        """
        if not data:
            data = {}

        client = WriterAIManager.acquire_client()
        passed_messages = cast(Iterable[Message], self.messages)

        response_data: Chat = client.chat.chat(messages=passed_messages, model=WriterAIManager.use_chat_model(), **{**data, **self.config})

        for entry in response_data.choices:
            message = entry.message
            if message:
                return message
        raise RuntimeError(f"Failed to acquire proper response for completion from data: {response_data}")

    def stream_complete(self, data: Optional['ChatOptions'] = None) -> Generator[dict, None, None]:
        """
        Initiates a stream to receive chunks of the model's reply.
        Note: in contrast with `Conversation.complete`, this method is not adding any messages to the conversation.

        :param data: Optional parameters to pass for processing.
        :yields: Model response chunks as they arrive from the stream.
        """
        if not data:
            data = {}

        client = WriterAIManager.acquire_client()
        passed_messages = cast(Iterable[Message], self.messages)

        response: Stream = client.chat.chat(messages=passed_messages, model=WriterAIManager.use_chat_model(), stream=True, **{**data, **self.config})

        # We avoid flagging first chunk
        # to trigger creating a message
        # to append chunks to
        flag_chunks = False

        for line in response:
            chunk = _process_chat_data_chunk(line)
            if flag_chunks is True:
                chunk |= {"chunk": True}
            if flag_chunks is False:
                flag_chunks = True
            yield chunk
        else:
            response.close()

    @property
    def serialized_messages(self) -> List['Message']:
        """
        Returns a representation of the conversation, excluding system messages.

        :return: List of messages without system messages.
        """
        # Excluding system messages for privacy & security reasons
        serialized_messages = \
            [message for message in self.messages if message["role"] != "system"]
        return serialized_messages


def complete(initial_text: str, data: Optional['CreateOptions'] = None) -> str:
    """
    Completes the input text using the given data and returns the first resulting text choice.

    :param initial_text: The initial text prompt for the completion.
    :param data: Optional dictionary containing parameters for the completion call.
    :return: The text of the first choice from the completion response.
    :raises RuntimeError: If response data was not properly formatted to retrieve model text.
    """
    if not data:
        data = {}

    client = WriterAIManager.acquire_client()

    response_data: Completion = client.completions.create(prompt=initial_text, model=WriterAIManager.use_completion_model(), **data)

    for entry in response_data.choices:
        text = entry.text
        if text:
            return text

    raise RuntimeError(f"Failed to acquire proper response for completion from data: {response_data}")


def stream_complete(initial_text: str, data: Optional['CreateOptions'] = None) -> Generator[str, None, None]:
    """
    Streams completion results from an initial text prompt, yielding each piece of text as it is received.

    :param initial_text: The initial text prompt for the stream completion.
    :param data: Optional dictionary containing parameters for the stream completion call.
    :yields: Each text completion as it arrives from the stream.
    """
    if not data:
        data = {"max_tokens": 2048}

    client = WriterAIManager.acquire_client()

    response: Stream = client.completions.create(prompt=initial_text, model=WriterAIManager.use_completion_model(), stream=True, **data)
    for line in response:
        processed_line = _process_completion_data_chunk(line)
        if processed_line:
            yield processed_line
    else:
        response.close()


def init(token: Optional[str] = None):
    """
    Initializes the WriterAIManager with an optional token.

    :param token: Optional token for authentication.
    :param url: Optional API URL to use for calls.
    :return: An instance of WriterAIManager.
    """
    return WriterAIManager(token=token)
