import logging
from datetime import datetime
from typing import (Generator, Iterable, List, Literal, Optional, TypedDict,
                    Union, cast)
from uuid import uuid4

from httpx import Timeout
from writerai import Writer
from writerai._exceptions import WriterError
from writerai._response import BinaryAPIResponse
from writerai._streaming import Stream
from writerai._types import Body, Headers, NotGiven, Query
from writerai.resources import FilesResource, GraphsResource
from writerai.types import Chat, Completion
from writerai.types import File as SDKFile
from writerai.types import FileDeleteResponse
from writerai.types import Graph as SDKGraph
from writerai.types import (GraphDeleteResponse,
                            GraphRemoveFileFromGraphResponse,
                            GraphUpdateResponse, StreamingData)
from writerai.types.chat_chat_params import Message as WriterAIMessage

from writer.core import get_app_process


class APIOptions(TypedDict, total=False):
    extra_headers: Optional[Headers]
    extra_query: Optional[Query]
    extra_body: Optional[Body]
    timeout: Union[float, Timeout, None, NotGiven]


class ChatOptions(APIOptions, total=False):
    model: str
    max_tokens: Union[int, NotGiven]
    n: Union[int, NotGiven]
    stop: Union[List[str], str, NotGiven]
    temperature: Union[float, NotGiven]
    top_p: Union[float, NotGiven]


class CreateOptions(APIOptions, total=False):
    model: str
    best_of: Union[int, NotGiven]
    max_tokens: Union[int, NotGiven]
    random_seed: Union[int, NotGiven]
    stop: Union[List[str], str, NotGiven]
    temperature: Union[float, NotGiven]
    top_p: Union[float, NotGiven]


class APIListOptions(APIOptions, total=False):
    after: Union[str, NotGiven]
    before: Union[str, NotGiven]
    limit: Union[int, NotGiven]
    order: Union[Literal["asc", "desc"], NotGiven]


logger = logging.Logger(__name__)


def _process_completion_data_chunk(choice: StreamingData) -> str:
    text = choice.value
    if isinstance(text, str):
        return text
    raise ValueError("Failed to retrieve text from completion stream")


def _process_chat_data_chunk(chat_data: Chat) -> dict:
    choices = chat_data.choices
    for entry in choices:
        dict_entry = cast(dict, entry)
        message = cast(dict, dict_entry["message"])
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


        :param token: Optional; the default token for API authentication used if WRITER_API_KEY environment variable is not set up.
        :raises RuntimeError: If an API key was not provided to initialize SDK client properly.
        """
        try:
            self.client = Writer(
                # This is the default and can be omitted
                api_key=token,
            )
        except WriterError:
            raise RuntimeError(
                "Failed to acquire Writer API key. " +
                "Provide it by either setting a WRITER_API_KEY" +
                " environment variable, or by initializing the" +
                " AI module explicitly: writer.ai.init(\"my-writer-api-key\")"
                ) from None
        current_process = get_app_process()
        setattr(current_process, 'ai_manager', self)

    @classmethod
    def acquire_instance(cls) -> 'WriterAIManager':
        """
        Retrieve the existing instance of WriterAIManager from the current app process.
        If no instance was previously initialized, creates a new one and attaches it to the current app process.

        :returns: The current instance of the manager.
        """
        instance: WriterAIManager
        current_process = get_app_process()

        # If instance was not created explicitly, we initialize a new one
        try:
            instance = getattr(current_process, 'ai_manager')
        except AttributeError:
            instance = cls()
        return instance

    @classmethod
    def authorize(cls, token: str):
        """
        Authorize the WriterAIManager with a new token.
        This can be done as an alternative to setting up an environment variable, or to override the token that was already provided before.

        :param token: The new token to use for authentication.
        """
        instance = cls.acquire_instance()
        instance.client = Writer(api_key=token)

    @classmethod
    def use_chat_model(cls) -> str:
        """
        Get the configuration for the chat model.

        :returns: Name for the chat model.
        """
        return "palmyra-x-002-32k"

    @classmethod
    def use_completion_model(cls) -> str:
        """
        Get the configuration for the completion model.

        :returns: Name for the completion model.
        """
        return "palmyra-x-002-instruct"

    @classmethod
    def acquire_client(cls) -> Writer:
        instance = cls.acquire_instance()
        return instance.client


class SDKWrapper:
    _wrapped: Union[SDKFile, SDKGraph]

    def _get_property(self, property_name):
        try:
            return getattr(self._wrapped, property_name)
        except AttributeError:
            raise AttributeError(
                f"type object '{self.__class__}' has no attribute {property_name}"
                ) from None


class Graph(SDKWrapper):
    _wrapped: SDKGraph = None
    stale_ids = set()

    def __init__(
            self,
            graph_object: SDKGraph
            ):
        self._wrapped = graph_object

    @staticmethod
    def _retrieve_graphs_accessor() -> GraphsResource:
        """
        Acquires the graphs accessor from the WriterAIManager singleton instance.

        :returns: The graphs accessor instance.
        """
        return WriterAIManager.acquire_client().graphs

    @property
    def id(self) -> str:
        return self._get_property('id')

    @property
    def created_at(self) -> datetime:
        return self._get_property('created_at')

    def _fetch_object_updates(self):
        if self.id in Graph.stale_ids:
            graphs = self._retrieve_graphs_accessor()
            fresh_object = graphs.retrieve(self.id)
            self._wrapped = fresh_object
            Graph.stale_ids.remove(self.id)

    @property
    def name(self) -> str:
        self._fetch_object_updates()
        return self._wrapped.name

    @property
    def description(self) -> Optional[str]:
        self._fetch_object_updates()
        return self._wrapped.description

    @property
    def file_status(self):
        self._fetch_object_updates()
        return self._wrapped.file_status

    def update(
            self,
            name: Optional[str] = None,
            description: Optional[str] = None,
            config: Optional[APIOptions] = None
            ) -> GraphUpdateResponse:
        config = config or {}

        # We use the payload dictionary
        # to distinguish between None-values
        # and NotGiven values
        payload = {}
        if name:
            payload["name"] = name
        if description:
            payload["description"] = description
        graphs = self._retrieve_graphs_accessor()
        response = graphs.update(self.id, **payload, **config)
        Graph.stale_ids.add(self.id)
        return response

    def add_file(
            self,
            file_id_or_file: Union['File', str],
            config: Optional[APIOptions] = None
            ) -> 'File':
        config = config or {}
        file_id = None
        if isinstance(file_id_or_file, File):
            file_id = file_id_or_file.id
        elif isinstance(file_id_or_file, str):
            file_id = file_id_or_file
        else:
            raise ValueError(
                "'Graph.add_file' method accepts either 'File' object" +
                f" or ID of file as string; got '{type(file_id_or_file)}'"
                )
        graphs = self._retrieve_graphs_accessor()
        response = graphs.add_file_to_graph(
            graph_id=self.id,
            file_id=file_id,
            **config
            )
        Graph.stale_ids.add(self.id)
        return File(response)

    def remove_file(
            self,
            file_id_or_file: Union['File', str],
            config: Optional[APIOptions] = None
            ) -> Optional[GraphRemoveFileFromGraphResponse]:
        config = config or {}
        file_id = None
        if isinstance(file_id_or_file, File):
            file_id = file_id_or_file.id
        elif isinstance(file_id_or_file, str):
            file_id = file_id_or_file
        else:
            raise ValueError(
                "'Graph.remove_file' method accepts either 'File' object" +
                f" or ID of file as string; got '{type(file_id_or_file)}'"
                )
        graphs = self._retrieve_graphs_accessor()
        response = graphs.remove_file_from_graph(
            graph_id=self.id,
            file_id=file_id
            )
        Graph.stale_ids.add(self.id)
        return response


def create_graph(
        name: str,
        description: Optional[str] = None,
        config: Optional[APIOptions] = None
        ) -> Graph:
    config = config or {}
    graphs = Graph._retrieve_graphs_accessor()
    graph_object = graphs.create(name=name, description=description, **config)
    graph = Graph(graph_object)
    return graph


def retrieve_graph(
        graph_id: str,
        config: Optional[APIListOptions] = None
        ) -> Graph:
    config = config or {}
    graphs = Graph._retrieve_graphs_accessor()
    graph_object = graphs.retrieve(graph_id, **config)
    graph = Graph(graph_object)
    return graph


def list_graphs(config: Optional[APIListOptions] = None) -> List[Graph]:
    config = config or {}
    graphs = Graph._retrieve_graphs_accessor()
    sdk_graphs = graphs.list(**config)
    return [Graph(sdk_graph) for sdk_graph in sdk_graphs]


def delete_graph(graph_id_or_graph: Union[Graph, str]) -> GraphDeleteResponse:
    graph_id = None
    if isinstance(graph_id_or_graph, Graph):
        graph_id = graph_id_or_graph.id
    elif isinstance(graph_id_or_graph, str):
        graph_id = graph_id_or_graph
    else:
        raise ValueError(
            "'delete_graph' method accepts either 'Graph' object" +
            f" or ID of graph as string; got '{type(graph_id_or_graph)}'"
            )
    graphs = Graph._retrieve_graphs_accessor()
    return graphs.delete(graph_id)


class File(SDKWrapper):
    _wrapped: SDKFile

    def __init__(self, file_object: SDKFile):
        self._wrapped = file_object

    @staticmethod
    def _retrieve_files_accessor() -> FilesResource:
        """
        Acquires the files client from the WriterAIManager singleton instance.

        :returns: The files client instance.
        """
        return WriterAIManager.acquire_client().files

    @property
    def id(self) -> str:
        return self._get_property('id')

    @property
    def created_at(self) -> datetime:
        return self._get_property('created_at')

    @property
    def graph_ids(self) -> List[str]:
        return self._get_property('graph_ids')

    @property
    def name(self) -> str:
        return self._get_property('name')

    def download(self) -> BinaryAPIResponse:
        files = self._retrieve_files_accessor()
        return files.download(self.id)


def retrieve_file(file_id: str, config: Optional[APIOptions] = None) -> File:
    config = config or {}
    files = File._retrieve_files_accessor()
    file_object = files.retrieve(file_id, **config)
    file = File(file_object)
    return file


def list_files(config: Optional[APIListOptions] = None) -> List[File]:
    config = config or {}
    files = File._retrieve_files_accessor()
    sdk_files = files.list(**config)
    return [File(sdk_file) for sdk_file in sdk_files]


def upload_file(
        data: bytes,
        type: str,
        name: Optional[str] = None,
        config: Optional[APIOptions] = None
        ) -> File:
    config = config or {}
    files = File._retrieve_files_accessor()
    uploaded_file = {
        "content": data,
        "content_type": type,
        "content_disposition":
            f'attachment;filename="{name or f"WF-{type}-{uuid4()}"}"'
        }
    sdk_file = files.upload(**uploaded_file, **config)
    return File(sdk_file)


def delete_file(
        file_id_or_file: Union['File', str],
        config: Optional[APIOptions] = None
        ) -> FileDeleteResponse:
    config = config or {}
    file_id = None
    if isinstance(file_id_or_file, File):
        file_id = file_id_or_file.id
    elif isinstance(file_id_or_file, str):
        file_id = file_id_or_file
    else:
        raise ValueError(
            "'delete_file' method accepts either 'File' object" +
            f" or ID of file as string; got '{type(file_id_or_file)}'"
            )

    files = File._retrieve_files_accessor()
    return files.delete(file_id, **config)


class Conversation:
    """
    Manages messages within a conversation flow with an AI system, including message validation,
    history management, and communication with an AI model.

    The Conversation class can be initialized in two ways:
    1. By providing an initial system prompt as a string. This starts a new conversation, adding a system message with the provided prompt.
       Example:
           >>> conversation = Conversation("You are a social media expert in the financial industry")
    2. By providing a history of messages as a list. This initializes the conversation with existing message data.
       Example:
           >>> history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi, how can I help?"}]
           >>> conversation = Conversation(history)

    The class supports both class-wide configuration, which affects the entire conversation, and call-specific configuration,
    which can override or complement the class-wide settings for specific method calls.

    :param prompt_or_history: Initial system prompt as a string, or history of messages as a list, used to start a new conversation or to load an existing one.
    :param config: Configuration settings for the conversation. These settings can include parameters such as `max_tokens`, `temperature`, and `timeout`,
                   which affect the behavior and performance of the conversation operations. This configuration provides a default context for all operations,
                   but can be overridden or extended by additional configurations passed directly to specific methods.

    Configuration Example:
        When initializing, you might provide a general configuration:
            >>> config = {'max_tokens': 100, 'temperature': 0.5}
            >>> conversation = Conversation("Initial prompt", config=config)

        Later, when calling `complete` or `stream_complete`, you can override or extend the initial configuration:
            >>> response = conversation.complete(data={'max_tokens': 150, 'temperature': 0.7})
        This would increase the `max_tokens` limit to 150 and adjust the `temperature` to 0.7 for this specific call.

    """
    class Message(TypedDict):
        """
        Typed dictionary for conversation messages.

        :param role: Specifies the sender role.
        :param content: Text content of the message.
        :param actions: Optional dictionary containing actions related to the message.
        """
        role: Literal["system", "assistant", "user"]
        content: str
        actions: Optional[dict]

    @classmethod
    def validate_message(cls, message):
        """
        Validates if the provided message dictionary matches the required structure and values.

        :param message: The message to validate.
        :raises ValueError: If the message structure is incorrect or values are inappropriate.
        """
        if not isinstance(message, dict):
            raise ValueError(f"Attempted to add a non-dict object to the Conversation: {message}")
        if not ("role" in message and "content" in message):
            raise ValueError(f"Improper message format to add to Conversation: {message}")
        if not (isinstance(message["content"], str)):
            raise ValueError(f"Non-string content in message cannot be added: {message}")
        if message["role"] not in ["system", "assistant", "user"]:
            raise ValueError(f"Unsupported role in message: {message}")

    def __init__(self, prompt_or_history: Optional[Union[str, List['Conversation.Message']]] = None, config: Optional[ChatOptions] = None):
        """
        Initializes a new conversation. Two options are possible:

        1. With a system prompt.

        :param system_prompt: The initial message from the system to start the conversation.
        :param config: Optional configuration settings for the conversation.

        Example:
        >>> conversation = Conversation("You are a social media expert in the financial industry")

        2. With a history of past messages.

        :param history_import: A list of messages that form the history of the conversation.
        :param config: Optional configuration settings for the conversation.

        Example:
        >>> history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi, how can I help?"}]
        >>> conversation = Conversation(history)
        """
        self.messages: List['Conversation.Message'] = []
        if isinstance(prompt_or_history, str):
            # Working with a prompt: adding a system message to history
            prompt = prompt_or_history
            self.add("system", prompt)
        elif isinstance(prompt_or_history, list):
            # Working with a history: trying to add messages
            history_import = prompt_or_history
            for message in history_import:
                self.validate_message(message)
                self += message

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

    @staticmethod
    def _prepare_message(message: 'Conversation.Message') -> WriterAIMessage:
        """
        Converts a message object stored in Conversation to a Writer AI SDK `Message` model, suitable for calls to API.

        :param raw_chunk: The data to be merged into the last message.
        :raises ValueError: If there are no messages in the conversation to merge with.
        """
        if not ("role" in message and "content" in message):
            raise ValueError("Improper message format")
        return WriterAIMessage(content=message["content"], role=message["role"])

    def __add__(self, chunk_or_message: Union['Conversation.Message', dict]):
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
            self.validate_message(message)
            self.messages.append({"role": message["role"], "content": message["content"], "actions": message.get("actions")})
        return self

    def add(self, role: str, message: str):
        """
        Adds a new message to the conversation.

        :param role: The role of the message sender.
        :param message: The content of the message.
        """
        self.__add__({"role": role, "content": message})

    def complete(self, config: Optional['ChatOptions'] = None) -> 'Conversation.Message':
        """
        Processes the conversation with the current messages and additional data to generate a response.
        Note: this method only produces AI model output and does not attach the result to the existing conversation history.

        :param config: Optional parameters to pass for processing.
        :return: Generated message.
        :raises RuntimeError: If response data was not properly formatted to retrieve model text.
        """
        config = config or {'max_tokens': 2048}

        client = WriterAIManager.acquire_client()
        passed_messages: Iterable[WriterAIMessage] = [self._prepare_message(message) for message in self.messages]
        request_data: ChatOptions = {**config, **self.config}
        request_model = request_data.get("model") or WriterAIManager.use_chat_model()

        response_data: Chat = client.chat.chat(
            messages=passed_messages,
            model=request_model,
            max_tokens=request_data.get('max_tokens', NotGiven()),
            n=request_data.get('n', NotGiven()),
            stop=request_data.get('stop', NotGiven()),
            temperature=request_data.get('temperature', NotGiven()),
            top_p=request_data.get('top_p', NotGiven()),
            extra_headers=request_data.get('extra_headers'),
            extra_query=request_data.get('extra_query'),
            extra_body=request_data.get('extra_body'),
            timeout=request_data.get('timeout', NotGiven())
            )

        for entry in response_data.choices:
            message = entry.message
            if message:
                return cast(Conversation.Message, message.model_dump())
        raise RuntimeError(f"Failed to acquire proper response for completion from data: {response_data}")

    def stream_complete(self, config: Optional['ChatOptions'] = None) -> Generator[dict, None, None]:
        """
        Initiates a stream to receive chunks of the model's reply.
        Note: this method only produces AI model output and does not attach the result to the existing conversation history.

        :param config: Optional parameters to pass for processing.
        :yields: Model response chunks as they arrive from the stream.
        """
        config = config or {'max_tokens': 2048}

        client = WriterAIManager.acquire_client()
        passed_messages: Iterable[WriterAIMessage] = [self._prepare_message(message) for message in self.messages]
        request_data: ChatOptions = {**config, **self.config}
        request_model = request_data.get("model") or WriterAIManager.use_chat_model()

        response: Stream = client.chat.chat(
            messages=passed_messages,
            model=request_model,
            stream=True,
            max_tokens=request_data.get('max_tokens', NotGiven()),
            n=request_data.get('n', NotGiven()),
            stop=request_data.get('stop', NotGiven()),
            temperature=request_data.get('temperature', NotGiven()),
            top_p=request_data.get('top_p', NotGiven()),
            extra_headers=request_data.get('extra_headers'),
            extra_query=request_data.get('extra_query'),
            extra_body=request_data.get('extra_body'),
            timeout=request_data.get('timeout'),
            )

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


def complete(initial_text: str, config: Optional['CreateOptions'] = None) -> str:
    """
    Completes the input text using the given data and returns the first resulting text choice.

    :param initial_text: The initial text prompt for the completion.
    :param config: Optional dictionary containing parameters for the completion call.
    :return: The text of the first choice from the completion response.
    :raises RuntimeError: If response data was not properly formatted to retrieve model text.
    """
    config = config or {}

    client = WriterAIManager.acquire_client()
    request_model = config.get("model", None) or WriterAIManager.use_completion_model()

    response_data: Completion = client.completions.create(
        model=request_model,
        prompt=initial_text,
        best_of=config.get("best_of", NotGiven()),
        max_tokens=config.get("max_tokens", NotGiven()),
        random_seed=config.get("random_seed", NotGiven()),
        stop=config.get("stop", NotGiven()),
        temperature=config.get("temperature", NotGiven()),
        top_p=config.get("top_p", NotGiven()),
        extra_headers=config.get("extra_headers"),
        extra_body=config.get("extra_body"),
        extra_query=config.get("extra_query"),
        timeout=config.get("timeout")
        )

    for entry in response_data.choices:
        text = entry.text
        if text:
            return text

    raise RuntimeError(f"Failed to acquire proper response for completion from data: {response_data}")


def stream_complete(initial_text: str, config: Optional['CreateOptions'] = None) -> Generator[str, None, None]:
    """
    Streams completion results from an initial text prompt, yielding each piece of text as it is received.

    :param initial_text: The initial text prompt for the stream completion.
    :param config: Optional dictionary containing parameters for the stream completion call.
    :yields: Each text completion as it arrives from the stream.
    """
    if not config:
        config = {"max_tokens": 2048}

    client = WriterAIManager.acquire_client()
    request_model = config.get("model", None) or WriterAIManager.use_completion_model()

    response: Stream = client.completions.create(
        model=request_model,
        prompt=initial_text,
        stream=True,
        best_of=config.get("best_of", NotGiven()),
        max_tokens=config.get("max_tokens", NotGiven()),
        random_seed=config.get("random_seed", NotGiven()),
        stop=config.get("stop", NotGiven()),
        temperature=config.get("temperature", NotGiven()),
        top_p=config.get("top_p", NotGiven()),
        extra_headers=config.get("extra_headers"),
        extra_body=config.get("extra_body"),
        extra_query=config.get("extra_query"),
        timeout=config.get("timeout")
        )

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
    :return: An instance of WriterAIManager.
    """
    return WriterAIManager(token=token)
