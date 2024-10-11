import json
import logging
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Set,
    TypedDict,
    Union,
    cast,
)
from uuid import uuid4

from httpx import Timeout
from writerai import Writer
from writerai._exceptions import WriterError
from writerai._response import BinaryAPIResponse
from writerai._streaming import Stream
from writerai._types import Body, Headers, NotGiven, Query
from writerai.resources import FilesResource, GraphsResource
from writerai.types import (
    Chat,
    Completion,
    FileDeleteResponse,
    GraphDeleteResponse,
    GraphRemoveFileFromGraphResponse,
    GraphUpdateResponse,
    StreamingData,
)
from writerai.types import File as SDKFile
from writerai.types import Graph as SDKGraph
from writerai.types.application_generate_content_params import Input
from writerai.types.chat import ChoiceMessage
from writerai.types.chat_chat_params import Message as WriterAIMessage
from writerai.types.chat_chat_params import ToolFunctionTool as SDKFunctionTool
from writerai.types.chat_chat_params import ToolGraphTool as SDKGraphTool

from writer.core import get_app_process


class APIOptions(TypedDict, total=False):
    extra_headers: Optional[Headers]
    extra_query: Optional[Query]
    extra_body: Optional[Body]
    timeout: Union[float, Timeout, None, NotGiven]


class ChatOptions(APIOptions, total=False):
    model: str
    tools: Union[Iterable[Union[SDKGraphTool, SDKFunctionTool]], NotGiven]
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


class Tool(TypedDict, total=False):
    type: str


class GraphTool(Tool):
    graph_ids: List[str]
    subqueries: bool


class FunctionTool(Tool):
    callable: Callable
    name: str
    parameters: Dict[str, Dict[str, str]]


logger = logging.Logger(__name__, level=logging.DEBUG)


def _process_completion_data_chunk(choice: StreamingData) -> str:
    text = choice.value
    if not text:
        return ""
    if isinstance(text, str):
        return text
    raise ValueError("Failed to retrieve text from completion stream")


def _process_chat_data_chunk(chat_data: Chat) -> dict:
    choices = chat_data.choices
    for entry in choices:
        dict_entry = entry.model_dump()
        if dict_entry.get("delta"):
            delta = cast(dict, dict_entry["delta"])

            # Provide content as empty string in case there is no diff
            delta["content"] = delta["content"] or ""
            return delta
        elif dict_entry.get("message"):
            message = cast(dict, dict_entry["message"])

            # Provide content as empty string in case there is no diff
            message["content"] = message["content"] or ""
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
        return "palmyra-x-004"

    @classmethod
    def use_completion_model(cls) -> str:
        """
        Get the configuration for the completion model.

        :returns: Name for the completion model.
        """
        return "palmyra-x-003-instruct"

    @classmethod
    def acquire_client(cls) -> Writer:
        instance = cls.acquire_instance()
        return instance.client


class SDKWrapper:
    """
    A wrapper class for SDK objects, allowing dynamic access to properties.

    Attributes:
        _wrapped (Union[SDKFile, SDKGraph]): The wrapped SDK object.
    """
    _wrapped: Union[SDKFile, SDKGraph]

    def _get_property(self, property_name):
        """
        Retrieves a property from the wrapped object.

        :param property_name: The name of the property to retrieve.
        :type property_name: str
        :returns: The value of the requested property.
        :raises AttributeError: If the property does not exist.
        """
        try:
            return getattr(self._wrapped, property_name)
        except AttributeError:
            raise AttributeError(
                f"type object '{self.__class__}' has no attribute {property_name}"
                ) from None


class Graph(SDKWrapper):
    """
    A wrapper class for SDKGraph objects, providing additional functionality.

    Attributes:
        _wrapped (writerai.types.Graph): The wrapped SDK Graph object.
        stale_ids (set): A set of stale graph IDs that need updates.
    """
    _wrapped: SDKGraph
    stale_ids: Set[str] = set()

    def __init__(
            self,
            graph_object: SDKGraph
            ):
        """
        Initializes the Graph with the given SDKGraph object.

        :param graph_object: The SDKGraph object to wrap.
        :type graph_object: writerai.types.Graph
        """
        self._wrapped = graph_object

    @staticmethod
    def _retrieve_graphs_accessor() -> GraphsResource:
        """
        Acquires the graphs accessor from the WriterAIManager singleton instance.

        :returns: The graphs accessor instance.
        :rtype: GraphsResource
        """
        return WriterAIManager.acquire_client().graphs

    @property
    def id(self) -> str:
        return self._get_property('id')

    @property
    def created_at(self) -> datetime:
        return self._get_property('created_at')

    def _fetch_object_updates(self):
        """
        Fetches updates for the graph object if it is stale.
        """
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
        """
        Updates the graph with the given parameters.

        :param name: The new name for the graph.
        :type name: Optional[str]
        :param description: The new description for the graph.
        :type description: Optional[str]
        :param config: Additional configuration options.
        :type config: Optional[APIOptions]
        :returns: The response from the update operation.
        :rtype: GraphUpdateResponse

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]): Additional headers for the request.
        - `extra_query` (Optional[Query]): Additional query parameters for the request.
        - `extra_body` (Optional[Body]): Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
        """
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
        """
        Adds a file to the graph.

        :param file_id_or_file: The file object or file ID to add.
        :type file_id_or_file: Union['File', str]
        :param config: Additional configuration options.
        :type config: Optional[APIOptions]
        :returns: The added file object.
        :rtype: File
        :raises ValueError: If the input is neither a File object nor a file ID string.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]): Additional headers for the request.
        - `extra_query` (Optional[Query]): Additional query parameters for the request.
        - `extra_body` (Optional[Body]): Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
        """
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
        """
        Removes a file from the graph.

        :param file_id_or_file: The file object or file ID to remove.
        :type file_id_or_file: Union['File', str]
        :param config: Additional configuration options.
        :type config: Optional[APIOptions]
        :returns: The response from the remove operation.
        :rtype: Optional[GraphRemoveFileFromGraphResponse]
        :raises ValueError: If the input is neither a File object nor a file ID string.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]): Additional headers for the request.
        - `extra_query` (Optional[Query]): Additional query parameters for the request.
        - `extra_body` (Optional[Body]): Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
        """
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
    """
    Creates a new graph with the given parameters.

    :param name: The name of the graph.
    :type name: str
    :param description: The description of the graph.
    :type description: Optional[str]
    :param config: Additional configuration options.
    :type config: Optional[APIOptions]
    :returns: The created graph object.
    :rtype: Graph

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]): Additional headers for the request.
    - `extra_query` (Optional[Query]): Additional query parameters for the request.
    - `extra_body` (Optional[Body]): Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
    """
    config = config or {}
    graphs = Graph._retrieve_graphs_accessor()
    graph_object = graphs.create(name=name, description=description or NotGiven(), **config)
    converted_object = cast(SDKGraph, graph_object)
    graph = Graph(converted_object)
    return graph


def retrieve_graph(
        graph_id: str,
        config: Optional[APIOptions] = None
        ) -> Graph:
    """
    Retrieves a graph by its ID.

    :param graph_id: The ID of the graph to retrieve.
    :type graph_id: str
    :param config: Additional configuration options.
    :type config: Optional[APIOptions]
    :returns: The retrieved graph object.
    :rtype: Graph

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]): Additional headers for the request.
    - `extra_query` (Optional[Query]): Additional query parameters for the request.
    - `extra_body` (Optional[Body]): Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
    """
    config = config or {}
    graphs = Graph._retrieve_graphs_accessor()
    graph_object = graphs.retrieve(graph_id, **config)
    graph = Graph(graph_object)
    return graph


def list_graphs(config: Optional[APIListOptions] = None) -> List[Graph]:
    """
    Lists all graphs with the given configuration.

    :param config: Additional configuration options.
    :type config: Optional[APIListOptions]
    :returns: A list of graph objects.
    :rtype: List[Graph]

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]): Additional headers for the request.
    - `extra_query` (Optional[Query]): Additional query parameters for the request.
    - `extra_body` (Optional[Body]): Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
    - `after` (Union[str, NotGiven]): Filter to retrieve items created after a specific cursor.
    - `before` (Union[str, NotGiven]): Filter to retrieve items created before a specific cursor.
    - `limit` (Union[int, NotGiven]): The number of items to retrieve.
    - `order` (Union[Literal["asc", "desc"], NotGiven]): The order in which to retrieve items.
    """
    config = config or {}
    graphs = Graph._retrieve_graphs_accessor()
    sdk_graphs = graphs.list(**config)
    return [Graph(sdk_graph) for sdk_graph in sdk_graphs]


def delete_graph(graph_id_or_graph: Union[Graph, str]) -> GraphDeleteResponse:
    """
    Deletes a graph by its ID or object.

    :param graph_id_or_graph: The graph object or graph ID to delete.
    :type graph_id_or_graph: Union[Graph, str]
    :returns: The response from the delete operation.
    :rtype: GraphDeleteResponse
    :raises ValueError: If the input is neither a Graph object nor a graph ID string.
    """
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
    """
    A wrapper class for SDK File objects, providing additional functionality.

    Attributes:
        _wrapped (writerai.types.File): The wrapped SDKFile object.
    """
    _wrapped: SDKFile

    def __init__(self, file_object: SDKFile):
        """
        Initializes the File with the given SDKFile object.

        :param file_object: The SDKFile object to wrap.
        :type file_object: writerai.types.File
        """
        self._wrapped = file_object

    @staticmethod
    def _retrieve_files_accessor() -> FilesResource:
        """
        Acquires the files client from the WriterAIManager singleton instance.

        :returns: The files client instance.
        :rtype: FilesResource
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
        """
        Downloads the file content.

        :returns: The response containing the file content.
        :rtype: BinaryAPIResponse
        """
        files = self._retrieve_files_accessor()
        return files.download(self.id)


def retrieve_file(file_id: str, config: Optional[APIOptions] = None) -> File:
    """
    Retrieves a file by its ID.

    :param file_id: The ID of the file to retrieve.
    :type file_id: str
    :param config: Additional configuration options.
    :type config: Optional[APIOptions]
    :returns: The retrieved file object.
    :rtype: writerai.types.File

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]): Additional headers for the request.
    - `extra_query` (Optional[Query]): Additional query parameters for the request.
    - `extra_body` (Optional[Body]): Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
    """
    config = config or {}
    files = File._retrieve_files_accessor()
    file_object = files.retrieve(file_id, **config)
    file = File(file_object)
    return file


def list_files(config: Optional[APIListOptions] = None) -> List[File]:
    """
    Lists all files with the given configuration.

    :param config: Additional configuration options.
    :type config: Optional[APIListOptions]
    :returns: A list of file objects.
    :rtype: List[File]

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]): Additional headers for the request.
    - `extra_query` (Optional[Query]): Additional query parameters for the request.
    - `extra_body` (Optional[Body]): Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
    - `after` (Union[str, NotGiven]): Filter to retrieve items created after a specific cursor.
    - `before` (Union[str, NotGiven]): Filter to retrieve items created before a specific cursor.
    - `limit` (Union[int, NotGiven]): The number of items to retrieve.
    - `order` (Union[Literal["asc", "desc"], NotGiven]): The order in which to retrieve items.
    """
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
    """
    Uploads a new file with the given parameters.

    :param data: The file content as bytes.
    :type data: bytes
    :param type: The MIME type of the file.
    :type type: str
    :param name: The name of the file.
    :type name: Optional[str]
    :param config: Additional configuration options.
    :type config: Optional[APIOptions]
    :returns: The uploaded file object.
    :rtype: writerai.types.File

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]): Additional headers for the request.
    - `extra_query` (Optional[Query]): Additional query parameters for the request.
    - `extra_body` (Optional[Body]): Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
    """
    config = config or {}
    files = File._retrieve_files_accessor()

    file_name = name or f"WF-{type}-{uuid4()}"
    content_disposition = f'attachment; filename="{file_name}"'

    # Now calling the upload method with correct types.
    sdk_file = files.upload(
        content=data,
        content_type=type,
        content_disposition=content_disposition
        )
    return File(sdk_file)


def delete_file(
        file_id_or_file: Union['File', str],
        config: Optional[APIOptions] = None
        ) -> FileDeleteResponse:
    """
    Deletes a file by its ID or object.

    :param file_id_or_file: The file object or file ID to delete.
    :type file_id_or_file: Union['File', str]
    :param config: Additional configuration options.
    :type config: Optional[APIOptions]
    :returns: The response from the delete operation.
    :rtype: FileDeleteResponse
    :raises ValueError: If the input is neither a File object nor a file ID string.

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]): Additional headers for the request.
    - `extra_query` (Optional[Query]): Additional query parameters for the request.
    - `extra_body` (Optional[Body]): Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]): Timeout for the request.
    """
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
    class Message(TypedDict, total=False):
        """
        Typed dictionary for conversation messages.

        :param role: Specifies the sender role.
        :param content: Text content of the message.
        :param actions: Optional dictionary containing actions related to the message.
        """
        role: Literal["system", "assistant", "user", "tool"]
        content: str
        actions: Optional[dict]
        name: Optional[str]
        tool_call_id: Optional[str]

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
        if not (isinstance(message["content"], str) or message["content"] is None):
            raise ValueError(f"Non-string content in message cannot be added: {message}")
        if message["role"] not in ["system", "assistant", "user", "tool"]:
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
        self._callable_registry: Dict = {}
        self._ongoing_tool_calls: Dict = {}

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
        sdk_message = WriterAIMessage(
            content=message["content"],
            role=message["role"]
            )
        if message.get("name"):
            sdk_message["name"] = cast(str, message["name"])
        if message.get("tool_call_id"):
            sdk_message["tool_call_id"] = cast(str, message["tool_call_id"])
        return sdk_message

    def _register_callable(
            self,
            callable_to_register: Callable,
            name: str,
            parameters: Dict[str, Dict[str, str]]
    ):
        """
        Internal helper function to store a provided callable for function call,
        to retrieve it when processing LLM response
        """
        if not callable(callable_to_register):
            raise ValueError(
                f"Expected `{name}` to be callable " +
                f"but got {type(callable_to_register)}"
                )
        self._callable_registry[name] = \
            {
                "callable": callable_to_register,
                "parameters": parameters
            }

    def _clear_callable_registry(self):
        """
        Clear callable registry after LLM response
        """
        self._callable_registry = {}

    def _clear_ongoing_tool_calls(self):
        self._ongoing_tool_calls = {}

    def _clear_tool_calls_helpers(self):
        self._clear_callable_registry()
        self._clear_ongoing_tool_calls()

    @property
    def _tool_calls_ready(self):
        calls_map = {
            index: "res" in ongoing_tool_call
            for index, ongoing_tool_call
            in self._ongoing_tool_calls.items()
            }
        return all(calls_map.values()) if calls_map else False

    def _gather_tool_calls_messages(self):
        return {
            index: ongoing_tool_call.get("res")
            for index, ongoing_tool_call
            in self._ongoing_tool_calls.items()
            }

    def _prepare_tool(
            self,
            tool_instance: Union['Graph', GraphTool, FunctionTool]
            ) -> Union[SDKGraphTool, SDKFunctionTool]:
        """
        Internal helper function to process a tool instance into the required format.
        """
        def validate_parameters(parameters: Dict[str, Dict[str, str]]) -> bool:
            """
            Validates the `parameters` dictionary to ensure that each key is a parameter name, 
            and each value is a dictionary containing at least a `type` field, and optionally a `description`.

            :param parameters: The parameters dictionary to validate.
            :return: True if valid, raises ValueError if invalid.
            """
            if not isinstance(parameters, dict):
                raise ValueError("`parameters` must be a dictionary")

            for param_name, param_info in parameters.items():
                if not isinstance(param_info, dict):
                    raise ValueError(f"Parameter '{param_name}' must be a dictionary")

                if "type" not in param_info:
                    raise ValueError(f"Parameter '{param_name}' must include a 'type' field")

                if not isinstance(param_info["type"], str):
                    raise ValueError(f"'type' for parameter '{param_name}' must be a string")

                # Optional 'description' validation (if provided)
                if "description" in param_info and not isinstance(param_info["description"], str):
                    raise ValueError(f"'description' for parameter '{param_name}' must be a string if provided")

            return True

        def validate_graph_ids(graph_ids: List[str]) -> bool:
            """
            Validates that `graph_ids` is a list of strings.

            :param graph_ids: The list of graph IDs to validate.
            :return: True if valid, raises ValueError if invalid.
            """
            if not isinstance(graph_ids, list):
                raise ValueError("`graph_ids` must be a list")

            for graph_id in graph_ids:
                if not isinstance(graph_id, str):
                    raise ValueError(f"Graph ID '{graph_id}' must be a string")

            return True

        if isinstance(tool_instance, Graph):
            # Prepare a single graph tool
            return cast(
                SDKGraphTool,
                {
                    "type": "graph",
                    "function": {
                        "graph_ids": [tool_instance.id],
                        "subqueries": True
                    }
                }
            )

        elif isinstance(tool_instance, dict):
            # Handle a dictionary (either a graph or a function)
            if "type" not in tool_instance:
                raise ValueError("Invalid tool definition: 'type' field is missing")

            tool_type = tool_instance["type"]

            if tool_type == "graph":
                tool_instance = cast(GraphTool, tool_instance)
                if "graph_ids" not in tool_instance:
                    raise ValueError("Graph tool must include 'graph_ids'")
                # Return graph tool JSON

                graph_ids_valid = validate_graph_ids(tool_instance["graph_ids"])
                if graph_ids_valid:
                    return cast(
                        SDKGraphTool,
                        {
                            "type": "graph",
                            "function": {
                                "graph_ids": tool_instance["graph_ids"],
                                "subqueries": tool_instance.get(
                                    "subqueries", False
                                    )
                            }
                        }
                    )
                else:
                    raise ValueError(
                        "Invalid Graph IDs provided: " +
                        f"{tool_instance['graph_ids']}"
                        )

            elif tool_type == "function":
                tool_instance = cast(FunctionTool, tool_instance)
                if "callable" not in tool_instance:
                    raise ValueError("Function tool missing `callable`")
                if "name" not in tool_instance or "parameters" not in tool_instance:
                    raise ValueError("Function tool must include 'name' and 'parameters'")

                parameters_valid = validate_parameters(tool_instance["parameters"])
                # Return function tool JSON
                if parameters_valid:
                    self._register_callable(
                        tool_instance["callable"],
                        tool_instance["name"],
                        tool_instance["parameters"]
                        )
                    return cast(
                        SDKFunctionTool,
                        {
                            "type": "function",
                            "function": {
                                "name": tool_instance["name"],
                                "parameters": tool_instance["parameters"]
                                }
                        }
                    )
                else:
                    raise ValueError(
                        "Invalid parameters for function " +
                        f"`{tool_instance['name']}`"
                        )

            else:
                raise ValueError(f"Unsupported tool type: {tool_type}")

        else:
            raise ValueError(f"Invalid tool input: {tool_instance}")

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

    def add(
            self,
            role: Literal["system", "assistant", "user", "tool"],
            message: str
            ):
        """
        Adds a new message to the conversation.

        :param role: The role of the message sender.
        :param message: The content of the message.
        """
        self.__add__({"role": role, "content": message})

    def _send_chat_request(
            self,
            passed_messages: Iterable[WriterAIMessage],
            request_model: str,
            request_data: ChatOptions,
            stream: bool = False
    ) -> Union[Stream, Chat]:
        """
        Helper function to send a chat request to the LLM.

        :param passed_messages: Messages to send in the request.
        :param request_model: Model to use for the chat.
        :param request_data: Configuration settings for the chat request.
        :param stream: Whether to use streaming mode.
        :return: The response from the LLM, either as a Stream or a Chat object.
        """
        client = WriterAIManager.acquire_client()
        logger.debug(
            "Attempting to request a message from LLM: " +
            f"passed_messages – {passed_messages}, " +
            f"request_data – {request_data}"
            )
        return client.chat.chat(
            messages=passed_messages,
            model=request_model,
            stream=stream,
            tools=request_data.get('tools', NotGiven()),
            max_tokens=request_data.get('max_tokens', NotGiven()),
            n=request_data.get('n', NotGiven()),
            stop=request_data.get('stop', NotGiven()),
            temperature=request_data.get('temperature', NotGiven()),
            top_p=request_data.get('top_p', NotGiven()),
            extra_headers=request_data.get('extra_headers'),
            extra_query=request_data.get('extra_query'),
            extra_body=request_data.get('extra_body'),
            timeout=request_data.get('timeout', NotGiven()),
        )

    def _convert_argument_to_type(self, value: Any, target_type: str) -> Any:
        """
        Converts the argument to the specified target type.

        :param value: The value to convert.
        :param target_type: The target type as a string.
        :return: The converted value.
        :raises ValueError: If the value cannot be converted to the target type.
        """
        if target_type == "string":
            return str(value)
        elif target_type == "integer":
            return int(value)
        elif target_type == "float":
            return float(value)
        elif target_type == "boolean":
            if isinstance(value, str):
                return value.lower() in ["true", "1"]
            return bool(value)
        elif target_type == "array":
            if isinstance(value, str):
                return json.loads(value)  # Assuming JSON string for arrays
            elif isinstance(value, list):
                return value
            else:
                raise ValueError(f"Cannot convert {value} to list.")
        elif target_type == "object":
            if isinstance(value, str):
                return json.loads(value)  # Assuming JSON string for objects
            elif isinstance(value, dict):
                return value
            else:
                raise ValueError(f"Cannot convert {value} to dict.")
        else:
            raise ValueError(f"Unsupported target type: {target_type}")

    def _execute_function_tool_call(self, index: int) -> dict:
        """
        Executes the function call for the specified tool call index.

        :param index: The index of the tool call in _ongoing_tool_calls.
        :return: The follow-up message to be sent to the LLM.
        """
        function_name = self._ongoing_tool_calls[index]["name"]
        arguments = self._ongoing_tool_calls[index]["arguments"]
        tool_call_id = self._ongoing_tool_calls[index]["tool_call_id"]

        # Parse arguments and execute callable
        try:
            parsed_arguments = json.loads(arguments)
            callable_entry = self._callable_registry.get(function_name)

            if callable_entry:
                param_specs = callable_entry["parameters"]
                # Convert arguments based on registered parameter types
                converted_arguments = {}
                for param_name, param_info in param_specs.items():
                    if param_name in parsed_arguments:
                        target_type = param_info["type"]
                        value = parsed_arguments[param_name]
                        converted_arguments[param_name] = self._convert_argument_to_type(value, target_type)
                    else:
                        raise ValueError(f"Missing required parameter: {param_name}")

                func = callable_entry.get("callable")
                if not func:
                    raise ValueError(f"Misconfigured function {function_name}: no callable provided")

                # Call the function with converted arguments
                try:
                    func_result = func(**converted_arguments)
                except Exception as e:
                    logger.error(
                        f"An error occured during the execution of function `{function_name}`: {e}"
                    )
                    func_result = "Function call failed"

                # Prepare follow-up message with the function call result
                follow_up_message = {
                    "role": "tool",
                    "name": function_name,
                    "tool_call_id": tool_call_id,
                    "content": func_result
                }

                return follow_up_message
            else:
                raise ValueError(f"`{function_name}` is not present in callable registry")

        except json.JSONDecodeError:
            logger.error("Failed to parse arguments for tool call")

        return {
                    "role": "tool",
                    "name": function_name,
                    "tool_call_id": tool_call_id,
                    "content": "Failed to parse arguments for tool call"
                }

    def _process_tool_call(self, index, tool_call_id, tool_call_name, tool_call_arguments):
        if index not in self._ongoing_tool_calls:
            self._ongoing_tool_calls[index] = {
                "name": None, "arguments": "", "tool_call_id": None
            }

        # Capture `tool_call_id` from the message
        if tool_call_id is not None:
            self._ongoing_tool_calls[index]["tool_call_id"] = tool_call_id

        # Capture `name` for function call
        if tool_call_name is not None:
            self._ongoing_tool_calls[index]["name"] = tool_call_name

        # Accumulate arguments across chunks
        if tool_call_arguments is not None:
            self._ongoing_tool_calls[index]["arguments"] += tool_call_arguments

        # Check if we have all necessary data to execute the function
        if (
            self._ongoing_tool_calls[index]["name"] is not None
            and self._ongoing_tool_calls[index]["arguments"].endswith("}")
        ):
            follow_up_message = self._execute_function_tool_call(index)
            if follow_up_message:
                self._ongoing_tool_calls[index]["res"] = follow_up_message

    def _process_tool_calls(self, message: ChoiceMessage):
        if message.tool_calls:
            for tool_call in message.tool_calls:
                index = tool_call.index
                tool_call_id = tool_call.id
                tool_call_name = tool_call.function.name
                tool_call_arguments = tool_call.function.arguments

                self._process_tool_call(
                    index,
                    tool_call_id,
                    tool_call_name,
                    tool_call_arguments
                )

    def _process_streaming_tool_calls(self, chunk: Dict):
        tool_calls = chunk["tool_calls"]
        if isinstance(tool_calls, list):
            for tool_call in tool_calls:
                index = tool_call["index"]
                tool_call_id = tool_call["id"]
                tool_call_name = tool_call["function"]["name"]
                tool_call_arguments = tool_call["function"]["arguments"]

                self._process_tool_call(
                    index,
                    tool_call_id,
                    tool_call_name,
                    tool_call_arguments
                )

    def _process_response_data(
            self,
            response_data: Chat,
            passed_messages: List[WriterAIMessage],
            request_model: str,
            request_data: ChatOptions,
            depth=1
            ) -> 'Conversation.Message':
        if depth > 3:
            raise RuntimeError("Reached maximum depth when processing response data tool calls.")
        for entry in response_data.choices:
            message = entry.message
            if message:
                # Handling tool call fragments
                logger.debug(f"Received message – {message}")
                if message.tool_calls is not None:
                    logger.debug(f"Message has tool calls - {message.tool_calls}")
                    self._process_tool_calls(message)
                    # Send follow-up call to LLM
                    logger.debug("Sending a request to LLM")
                    finalized_messages = passed_messages + [
                                self._prepare_message(message)
                                for message in self._gather_tool_calls_messages().values()
                                ]
                    follow_up_response = cast(
                        Chat,
                        self._send_chat_request(
                            passed_messages=finalized_messages,
                            request_model=request_model,
                            request_data=request_data
                        )
                    )
                    logger.debug(f"Received response – {follow_up_response}")

                    # Clear buffer and callable registry for the completed tool call
                    self._clear_tool_calls_helpers()

                    # Call the function recursively to either process a new tool call
                    # or return the message if no tool calls are requested
                    return self._process_response_data(
                        follow_up_response,
                        passed_messages=passed_messages,
                        request_model=request_model,
                        request_data=request_data,
                        depth=depth+1
                        )
                else:
                    return cast(Conversation.Message, message.model_dump())
        raise RuntimeError(f"Failed to acquire proper response for completion from data: {response_data}")

    def _process_stream_response(
            self,
            response: Stream,
            passed_messages: List[WriterAIMessage],
            request_model: str,
            request_data: ChatOptions,
            depth=1,
            flag_chunks=False
    ) -> Generator[dict, None, None]:
        if depth > 3:
            raise RuntimeError("Reached maximum depth when processing response data tool calls.")
        # We avoid flagging first chunk
        # to trigger creating a message
        # to append chunks to

        for line in response:
            chunk = _process_chat_data_chunk(line)

            # Handling tool call fragments
            if chunk.get("tool_calls") is not None:
                self._process_streaming_tool_calls(chunk)
                if self._tool_calls_ready:
                    # Send follow-up call to LLM
                    passed_messages = passed_messages + [
                            self._prepare_message(message)
                            for message in self._gather_tool_calls_messages().values()
                            ]
                    follow_up_response = cast(
                        Stream,
                        self._send_chat_request(
                            passed_messages=passed_messages,
                            request_model=request_model,
                            request_data=request_data,
                            stream=True
                        )
                    )

                    # Clear buffer and callable registry for the completed tool call
                    try:
                        self._clear_tool_calls_helpers()
                        yield from self._process_stream_response(
                            response=follow_up_response,
                            passed_messages=passed_messages,
                            request_model=request_model,
                            request_data=request_data,
                            depth=depth+1,
                            flag_chunks=True
                        )
                    finally:
                        follow_up_response.close()

            else:
                # Handle regular message chunks
                if flag_chunks is True:
                    chunk |= {"chunk": True}
                if flag_chunks is False:
                    flag_chunks = True
                yield chunk

    def complete(
            self,
            config: Optional['ChatOptions'] = None,
            tools: Optional[
                Union[
                    Graph,
                    GraphTool,
                    FunctionTool,
                    List[Union[Graph, GraphTool, FunctionTool]]
                    ]  # can be an instance of tool or a list of instances
                ] = None
            ) -> 'Conversation.Message':
        """
        Processes the conversation with the current messages and additional data to generate a response.
        Note: this method only produces AI model output and does not attach the result to the existing conversation history.

        :param config: Optional parameters to pass for processing.
        :return: Generated message.
        :raises RuntimeError: If response data was not properly formatted to retrieve model text.
        """
        config = config or {'max_tokens': 1024}
        if tools is not None and not isinstance(tools, list):
            tools = [tools]

        prepared_tools = [
            self._prepare_tool(tool_instance) for tool_instance in (tools or [])
            ]

        passed_messages: List[WriterAIMessage] = [self._prepare_message(message) for message in self.messages]
        request_data: ChatOptions = {**config, **self.config}
        if prepared_tools:
            request_data |= {"tools": prepared_tools}
        request_model = request_data.get("model") or WriterAIManager.use_chat_model()

        response_data: Chat = cast(
                Chat,
                self._send_chat_request(
                    passed_messages=passed_messages,
                    request_model=request_model,
                    request_data=request_data
                )
            )

        return self._process_response_data(
            response_data,
            passed_messages=passed_messages,
            request_model=request_model,
            request_data=request_data
            )

    def stream_complete(
            self,
            config: Optional['ChatOptions'] = None,
            tools: Optional[
                Union[
                    Graph,
                    GraphTool,
                    FunctionTool,
                    List[Union[Graph, GraphTool, FunctionTool]]
                    ]  # can be an instance of tool or a list of instances
                ] = None
            ) -> Generator[dict, None, None]:
        """
        Initiates a stream to receive chunks of the model's reply.
        Note: this method only produces AI model output and does not attach the result to the existing conversation history.

        :param config: Optional parameters to pass for processing.
        :yields: Model response chunks as they arrive from the stream.
        """
        config = config or {}
        if tools is not None and not isinstance(tools, list):
            tools = [tools]

        prepared_tools = [
            self._prepare_tool(tool_instance)
            for tool_instance in (tools or [])
            ]

        passed_messages: List[WriterAIMessage] = \
            [self._prepare_message(message) for message in self.messages]
        request_data: ChatOptions = {**config, **self.config}
        if prepared_tools:
            request_data |= {"tools": prepared_tools}
        request_model = \
            request_data.get("model") or WriterAIManager.use_chat_model()

        response: Stream = cast(
            Stream,
            self._send_chat_request(
                passed_messages=passed_messages,
                request_model=request_model,
                request_data=request_data,
                stream=True
            )
        )

        yield from self._process_stream_response(
            response=response,
            passed_messages=passed_messages,
            request_model=request_model,
            request_data=request_data
        )

        response.close()

    @property
    def serialized_messages(self) -> List['Message']:
        """
        Returns a representation of the conversation, excluding system messages.

        :return: List of messages without system messages.
        """
        # Excluding system messages for privacy & security reasons
        serialized_messages = \
            [message for message in self.messages if message["role"] not in ["system", "tool"]]
        return serialized_messages


class Apps:
    def generate_content(
            self,
            application_id: str,
            input_dict: Optional[Dict[str, str]] = None,
            config: Optional[APIOptions] = None) -> str:
        """
        Generates output based on an existing AI Studio no-code application.

        :param application_id: The id for the application, which can be obtained on AI Studio.
        :param input_dict: Optional dictionary containing parameters for the generation call.
        :return: The generated text.
        :raises RuntimeError: If response data was not properly formatted to retrieve model text.
        """

        client = WriterAIManager.acquire_client()
        config = config or {}
        input_dict = input_dict or {}
        inputs = []

        for k, v in input_dict.items():
            inputs.append(Input({
                "id": k,
                "value": v if isinstance(v, list) else [v]
            }))

        response_data = client.applications.generate_content(
            application_id=application_id,
            inputs=inputs,
            **config
            )

        text = response_data.suggestion
        if text:
            return text

        raise RuntimeError(
            "Failed to acquire proper response for completion from data: " +
            f"{response_data}"
            )


def complete(
        initial_text: str,
        config: Optional['CreateOptions'] = None
        ) -> str:
    """
    Completes the input text using the given data and returns the first resulting text choice.

    :param initial_text: The initial text prompt for the completion.
    :param config: Optional dictionary containing parameters for the completion call.
    :return: The text of the first choice from the completion response.
    :raises RuntimeError: If response data was not properly formatted to retrieve model text.
    """
    config = config or {}

    client = WriterAIManager.acquire_client()
    request_model = \
        config.get("model", None) or WriterAIManager.use_completion_model()

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

    raise RuntimeError(
        "Failed to acquire proper response for completion from data: " +
        f"{response_data}")


def stream_complete(
        initial_text: str,
        config: Optional['CreateOptions'] = None
        ) -> Generator[str, None, None]:
    """
    Streams completion results from an initial text prompt, yielding each piece of text as it is received.

    :param initial_text: The initial text prompt for the stream completion.
    :param config: Optional dictionary containing parameters for the stream completion call.
    :yields: Each text completion as it arrives from the stream.
    """
    config = config or {}

    client = WriterAIManager.acquire_client()
    request_model = \
        config.get("model", None) or WriterAIManager.use_completion_model()

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


apps = Apps()
