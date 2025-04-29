import json
import logging
from contextvars import ContextVar
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
from writerai import DefaultHttpxClient, Writer
from writerai._exceptions import WriterError
from writerai._response import BinaryAPIResponse
from writerai._streaming import Stream
from writerai._types import Body, Headers, NotGiven, Query
from writerai.resources import FilesResource, GraphsResource
from writerai.types import (
    ApplicationListResponse,
    ApplicationRetrieveResponse,
    ChatCompletion,
    Completion,
    CompletionChunk,
    FileDeleteResponse,
    GraphDeleteResponse,
    GraphRemoveFileFromGraphResponse,
    GraphUpdateResponse,
)
from writerai.types import File as SDKFile
from writerai.types import Graph as SDKGraph
from writerai.types.application_generate_content_params import Input
from writerai.types.applications import (
    ApplicationGenerateAsyncResponse,
    JobCreateResponse,
    JobRetryResponse,
)
from writerai.types.applications.application_graphs_response import ApplicationGraphsResponse
from writerai.types.chat_chat_params import GraphData, ToolChoice
from writerai.types.chat_chat_params import Message as WriterAIMessage
from writerai.types.chat_completion_message import ChatCompletionMessage
from writerai.types.question import Question
from writerai.types.question_response_chunk import QuestionResponseChunk
from writerai.types.shared_params.tool_param import FunctionTool as SDKFunctionTool
from writerai.types.shared_params.tool_param import GraphTool as SDKGraphTool
from writerai.types.shared_params.tool_param import LlmTool as SDKLlmTool

from writer.core import get_app_process

DEFAULT_CHAT_MODEL = "palmyra-x-004"
DEFAULT_COMPLETION_MODEL = "palmyra-x-004"


_ai_client: ContextVar[Optional[Writer]] = ContextVar("ai_client", default=None)


class APIOptions(TypedDict, total=False):
    extra_headers: Optional[Headers]
    extra_query: Optional[Query]
    extra_body: Optional[Body]
    timeout: Union[float, Timeout, None, NotGiven]


class ChatOptions(APIOptions, total=False):
    model: str
    tool_choice: ToolChoice
    tools: Union[
            Iterable[
                Union[SDKGraphTool, SDKFunctionTool, SDKLlmTool]
                ],
            NotGiven
        ]
    logprobs: Union[bool, NotGiven]
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


class APIRetrieveJobsOptions(APIOptions, total=False):
    limit: Union[int, NotGiven]
    offset: Union[int, NotGiven]
    status: Union[
        Literal["completed", "failed", "in_progress"],
        NotGiven
        ]


class Tool(TypedDict, total=False):
    type: str


class GraphTool(Tool):
    graph_ids: List[str]
    subqueries: bool
    description: Optional[str]


class FunctionToolParameterMeta(TypedDict):
    type: Union[
        Literal["string"],
        Literal["number"],
        Literal["integer"],
        Literal["float"],
        Literal["boolean"],
        Literal["array"],
        Literal["object"],
        Literal["null"]
        ]
    description: Optional[str]
    required: Optional[bool]


class FunctionTool(Tool):
    callable: Callable
    name: str
    description: Optional[str]
    parameters: Dict[str, FunctionToolParameterMeta]


def create_function_tool(
    callable: Callable,
    name: str,
    parameters: Optional[Dict[str, FunctionToolParameterMeta]] = None,
    description: Optional[str] = None
) -> FunctionTool:
    parameters = parameters or {}
    return FunctionTool(
        type="function",
        callable=callable,
        name=name,
        description=description,
        parameters=parameters
    )


class LLMTool(Tool):
    model: str
    description: str


def _process_completion_data_chunk(choice: CompletionChunk) -> str:
    text = choice.value
    if not text:
        return ""
    if isinstance(text, str):
        return text
    raise ValueError("Failed to retrieve text from completion stream")


def _process_chat_data_chunk(chat_data: ChatCompletion) -> tuple[dict, dict]:
    choices = chat_data.choices
    for entry in choices:
        dict_entry = entry.model_dump()
        if dict_entry.get("delta"):
            delta = cast(dict, dict_entry["delta"])

            # Provide content as empty string in case there is no diff
            delta["content"] = delta["content"] or ""
            return dict_entry, delta
        elif dict_entry.get("message"):
            message = cast(dict, dict_entry["message"])

            # Provide content as empty string in case there is no diff
            message["content"] = message["content"] or ""
            return dict_entry, message
    raise ValueError("Failed to retrieve text from chat stream")


class WriterAIManager:
    """
    Manages authentication for Writer AI functionalities.

    :ivar token: Authentication token for the Writer AI API.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initializes a WriterAIManager instance.


        :param token: Optional; the default token for API authentication used
        if WRITER_API_KEY environment variable is not set up.
        :raises RuntimeError: If an API key was not provided to initialize
        SDK client properly.
        """
        self.token = token
        from writer.core import get_app_process
        current_process = get_app_process()
        setattr(current_process, 'ai_manager', self)

    @classmethod
    def acquire_instance(cls) -> 'WriterAIManager':
        """
        Retrieve the existing instance of WriterAIManager from
        the current app process.
        If no instance was previously initialized, creates a new one and
        attaches it to the current app process.

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
        This can be done as an alternative to setting up an environment
        variable, or to override the token that was already provided before.

        :param token: The new token to use for authentication.
        """
        instance = cls.acquire_instance()
        instance.token = token

    @classmethod
    def use_chat_model(cls) -> str:
        """
        Get the configuration for the chat model.

        :returns: Name for the chat model.
        """
        return DEFAULT_CHAT_MODEL

    @classmethod
    def use_completion_model(cls) -> str:
        """
        Get the configuration for the completion model.

        :returns: Name for the completion model.
        """
        return DEFAULT_COMPLETION_MODEL

    @classmethod
    def acquire_client(
        cls,
        custom_httpx_client: Optional[DefaultHttpxClient] = None,
        force_new_client: Optional[bool] = False
    ) -> Writer:
        from writer.core import get_session
        instance = cls.acquire_instance()

        # Acquire header from session
        # and set it to the client

        current_session = get_session()
        custom_headers = {}

        if current_session:
            headers = current_session.headers or {}
            agent_token_header = headers.get("x-agent-token")
            if agent_token_header:
                custom_headers = {
                        "X-Agent-Token": agent_token_header
                    }

        try:
            context_client = _ai_client.get(None)
            if force_new_client or not context_client:
                client = Writer(
                    api_key=instance.token,
                    default_headers=custom_headers,
                    http_client=custom_httpx_client
                    )
                _ai_client.set(client)
                return client
            else:
                return context_client
        except WriterError:
            raise RuntimeError(
                "Failed to acquire Writer API key. " +
                "Provide it by either setting a WRITER_API_KEY" +
                " environment variable, or by initializing the" +
                " AI module explicitly: writer.ai.init(\"my-writer-api-key\")"
                ) from None


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
                f"type object '{self.__class__}' " +
                f"has no attribute {property_name}"
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
        Acquires the graphs accessor from the WriterAIManager
        singleton instance.

        :returns: The graphs accessor instance.
        :rtype: GraphsResource
        """
        return WriterAIManager.acquire_client().graphs

    @property
    def is_stale(self):
        return self.id in Graph.stale_ids

    @property
    def id(self) -> str:
        return self._get_property('id')

    @property
    def created_at(self) -> datetime:
        return self._get_property('created_at')

    def _fetch_object_updates(self, force=False):
        """
        Fetches updates for the graph object if it is stale.
        """
        def _get_fresh_object():
            graphs = self._retrieve_graphs_accessor()
            fresh_object = graphs.retrieve(self.id)
            self._wrapped = fresh_object

        if self.is_stale or force is True:
            _get_fresh_object()
        if self.is_stale:
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
        self._fetch_object_updates(force=True)
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
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.
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
        :raises ValueError: If the input is neither a File object
        nor a file ID string.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.
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
        :raises ValueError: If the input is neither a File object
        nor a file ID string.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.
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
            file_id=file_id,
            **config
            )
        Graph.stale_ids.add(self.id)
        return response

    def _question(
        self,
        question: str,
        stream: bool = True,
        subqueries: bool = False,
        config: Optional[APIOptions] = None
    ):
        if question == "":
            logging.warning(
                'Using empty `question` string ' +
                'against `graphs.question` resource. ' +
                'The model is not likely to produce a meaningful response.'
                )
        config = config or {}
        graphs = self._retrieve_graphs_accessor()
        response = graphs.question(
                graph_ids=[self.id,],
                question=question,
                subqueries=subqueries,
                stream=stream,
                **config
            )
        return response

    def stream_ask(
            self,
            question: str,
            subqueries: bool = False,
            config: Optional[APIOptions] = None
    ) -> Generator[str, None, None]:
        """
        Streams response for a question posed to the graph.

        This method returns incremental chunks of the response, ideal for long
        responses or when reduced latency is needed.

        :param question: The query or question to be answered by the graph.
        :param subqueries: Enables subquery generation if set to True,
        enhancing the result.
        :param config: Optional dictionary for additional API
        configuration settings.

        :yields: Incremental chunks of the answer to the question.

        :raises ValueError: If an invalid graph or graph ID
        is provided in `graphs_or_graph_ids`.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.

        **Example Usage**:

        >>> for chunk in graph.stream_ask(
        ...     question="What are the benefits of renewable energy?"
        ... ):
        ...     print(chunk)
        ...
        """

        response = cast(
                Stream[QuestionResponseChunk],
                self._question(
                    question=question,
                    subqueries=subqueries,
                    stream=True,
                    config=config
                )
            )
        for chunk in response._iter_events():
            raw_data = chunk.data
            answer = ""
            try:
                data = json.loads(raw_data)
                answer = data.get("answer", "")
            except json.JSONDecodeError:
                logging.error(
                    "Couldn't parse chunk data during `question` streaming"
                    )
            yield answer

    def ask(
            self,
            question: str,
            subqueries: bool = False,
            config: Optional[APIOptions] = None
    ):
        """
        Sends a question to the graph and retrieves
        a single response.

        :param question: The query or question to be answered by the graph.
        :param subqueries: Enables subquery generation if set to True,
        enhancing the result.
        :param config: Optional dictionary for additional API
        configuration settings.

        :return: The answer to the question from the graph(s).

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.

        **Example Usage**:

        >>> response = graph.ask(
        ...     question="What is the capital of France?",
        ... )
        """
        response = cast(
            Question,
            self._question(
                question=question,
                subqueries=subqueries,
                stream=False,
                config=config
                )
            )
        return response.answer


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
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.
    """
    config = config or {}
    graphs = Graph._retrieve_graphs_accessor()
    graph_object = graphs.create(
        name=name,
        description=description or NotGiven(),
        **config
        )
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
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.
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
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.
    - `after` (Union[str, NotGiven]):
    Filter to retrieve items created after a specific cursor.
    - `before` (Union[str, NotGiven]):
    Filter to retrieve items created before a specific cursor.
    - `limit` (Union[int, NotGiven]):
    The number of items to retrieve.
    - `order` (Union[Literal["asc", "desc"], NotGiven]):
    The order in which to retrieve items.
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
    :raises ValueError: If the input is neither a Graph object
    nor a graph ID string.
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
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.
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
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.
    - `after` (Union[str, NotGiven]):
    Filter to retrieve items created after a specific cursor.
    - `before` (Union[str, NotGiven]):
    Filter to retrieve items created before a specific cursor.
    - `limit` (Union[int, NotGiven]):
    The number of items to retrieve.
    - `order` (Union[Literal["asc", "desc"], NotGiven]):
    The order in which to retrieve items.
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
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.
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
    :raises ValueError: If the input is neither a File object
    nor a file ID string.

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.
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
    Manages messages within a conversation flow with an AI system,
    including message validation, history management, and communication
    with an AI model.

    The Conversation class can be initialized in two ways:
    1. By providing an initial system prompt as a string. This starts a new
       conversation, adding a system message with the provided prompt.
       Example:

        >>> conversation = Conversation(
        ...         "You are a social media expert in the financial industry"
        ...         )

    2. By providing a history of messages as a list. This initializes
       the conversation with existing message data.
       Example:

        >>> history = [
        ...         {"role": "user", "content": "Hello"},
        ...         {"role": "assistant", "content": "Hi, how can I help?"}
        ...         ]
        >>> conversation = Conversation(history)

    The class supports both class-wide configuration, which affects
    the entire conversation, and call-specific configuration,
    which can override or complement the class-wide settings
    for specific method calls.

    :param prompt_or_history: Initial system prompt as a string, or
                              history of messages as a list, used to start
                              a new conversation or to load an existing one.
    :param config: Configuration settings for the conversation.

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.
    - `model` (str):
    The model to use for completion.
    - `tool_choice` (ToolChoice):
    Configure how the model will call functions: `auto` will allow the model
    to automatically choose the best tool, `none` disables tool calling.
    You can also pass a specific previously defined function.
    - `logprobs` (Union[bool, NotGiven]):
    Specifies whether to return log probabilities of the output tokens.
    - `tools` (Union[Iterable[Union[SDKGraphTool,
    SDKFunctionTool, SDKLlmTool]], NotGiven]):
    Tools available for the model to use.
    - `max_tokens` (Union[int, NotGiven]):
    Maximum number of tokens to generate.
    - `n` (Union[int, NotGiven]):
    Number of completions to generate.
    - `stop` (Union[List[str], str, NotGiven]):
    Sequences where the API will stop generating tokens.
    - `temperature` (Union[float, NotGiven]):
    Controls the randomness or creativity of the model's responses.
    A higher temperature results in more varied and less predictable text,
    while a lower temperature produces more deterministic
    and conservative outputs.
    - `top_p` (Union[float, NotGiven]):
    Sets the threshold for "nucleus sampling," a technique to focus the model's
    token generation on the most likely subset of tokens. Only tokens with
    cumulative probability above this threshold are considered, controlling the
    trade-off between creativity and coherence.

    **Configuration Example:**

    When initializing, you might provide a general configuration:

    >>> config = {'max_tokens': 100, 'temperature': 0.5}

    >>> conversation = Conversation("Initial prompt", config=config)

    Later, when calling `complete` or `stream_complete`, you can override
    or extend the initial configuration:

    >>> response = conversation.complete(
    ...             config={
    ...                 'max_tokens': 150,
    ...                 'temperature': 0.7
    ...                 }
    ...             )

    This would increase the `max_tokens` limit to 150 and adjust
    the `temperature` to 0.7 for this specific call.

    """
    class Message(TypedDict, total=False):
        """
        Typed dictionary for conversation messages.

        :param role: Specifies the sender role.
        :param content: Text content of the message.
        :param actions: Optional dictionary containing actions
        related to the message.
        """
        role: Literal["system", "assistant", "user", "tool"]
        content: str
        actions: Optional[dict]
        name: Optional[str]
        tool_call_id: Optional[str]
        tool_calls: Optional[List[Dict[str, Union[int, Dict]]]]

    @classmethod
    def validate_message(cls, message):
        """
        Validates if the provided message dictionary matches
        the required structure and values.

        :param message: The message to validate.
        :raises ValueError: If the message structure is incorrect
        or values are inappropriate.
        """
        if not isinstance(message, dict):
            raise ValueError(
                "Attempted to add a non-dict object" +
                f"to the Conversation: {message}"
                )

        if not ("role" in message and "content" in message):
            raise ValueError(
                f"Improper message format to add to Conversation: {message}"
                )

        if not (
            isinstance(message["content"], str)
            or
            message["content"] is None
        ):
            raise ValueError(
                f"Non-string content in message cannot be added: {message}"
                )

        if message["role"] not in ["system", "assistant", "user", "tool"]:
            raise ValueError(f"Unsupported role in message: {message}")

    def __init__(
            self,
            prompt_or_history: Optional[
                Union[str, List['Conversation.Message']]
                ] = None,
            config: Optional[ChatOptions] = None
            ):
        """
        Initializes a new conversation. Two options are possible:

        1. With a system prompt.

        :param system_prompt: The initial message from the system
        to start the conversation.
        :param config: Optional configuration settings for the conversation.

        Example:
        >>> conversation = Conversation(
        ...     "You are a social media expert in the financial industry"
        ...     )

        2. With a history of past messages.

        :param history_import: A list of messages that form the history
        of the conversation.
        :param config: Optional configuration settings for the conversation.

        Example:
        >>> history = [
        ...     {"role": "user", "content": "Hello"},
        ...     {"role": "assistant", "content": "Hi, how can I help?"}
        ...     ]
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

        This method takes a chunk of data and integrates it into the content
        of the last message of the conversation. It appends additional content
        if present, and merges other key-value pairs into the last message's
        dictionary.

        :param raw_chunk: A dictionary containing the chunk of data
        to be merged.
        :raises ValueError: If the Conversation's `messages` list is empty,
        indicating there is no message to merge the chunk with.
        """
        def _clear_chunk_flag(chunk):
            return {
                key: value
                for key, value in chunk.items()
                if key != "chunk"
                }

        if not self.messages:
            raise ValueError("No message to merge chunk with")
        clear_chunk = _clear_chunk_flag(raw_chunk)
        updated_last_message: 'Conversation.Message' = self.messages[-1]
        if "content" in clear_chunk:
            updated_last_message["content"] += clear_chunk.pop("content") or ""

        if "tool_calls" in clear_chunk:
            # Ensure 'tool_calls' exists in updated_last_message as list
            if (
                "tool_calls" not in updated_last_message
                or updated_last_message["tool_calls"] is None
            ):
                updated_last_message["tool_calls"] = []
            # Get the list of new tool calls
            new_tool_calls = clear_chunk.pop("tool_calls", []) or []

            for new_call in new_tool_calls:
                last_message_tool_calls = \
                    cast(list, updated_last_message["tool_calls"])
                if not new_call.get("id"):
                    # Received ID is an indicator
                    # of a new call that needs to be added:
                    # otherwise, modify the latest existing call
                    existing_call = last_message_tool_calls[-1]
                    for key, value in new_call.items():
                        if key == "function":
                            if key not in existing_call:
                                existing_call[key] = {}
                            call_function = existing_call[key]
                            # Iterate over function keys and values
                            for fkey, fvalue in value.items():
                                if fkey == "arguments":
                                    # Ensure "arguments" are present
                                    # in existing call as string
                                    if (
                                        fkey not in call_function
                                        or
                                        call_function[fkey] is None
                                    ):
                                        call_function[fkey] = ""

                                    # Append the arguments value
                                    # or an empty string
                                    # to existing arguments
                                    call_function[fkey] += \
                                        fvalue or ""
                                elif fvalue is not None and fvalue != '':
                                    call_function[fkey] = fvalue
                        elif value is not None and value != '':
                            existing_call[key] = value
                else:
                    # If ID was received, this is the new call and we add it
                    last_message_tool_calls.append(new_call)

        updated_last_message |= clear_chunk

    @staticmethod
    def _prepare_message(message: 'Conversation.Message') -> WriterAIMessage:
        """
        Converts a message object stored in Conversation to a Writer AI SDK
        `Message` model, suitable for calls to API.

        :param raw_chunk: The data to be merged into the last message.
        :raises ValueError: If there are no messages in the conversation
        to merge with.
        """
        if not ("role" in message and "content" in message):
            raise ValueError("Improper message format")
        sdk_message = WriterAIMessage(
            content=message.get("content", None) or "",
            role=message["role"]
            )
        if msg_name := message.get("name"):
            sdk_message["name"] = cast(str, msg_name)
        if msg_tool_call_id := message.get("tool_call_id"):
            sdk_message["tool_call_id"] = cast(str, msg_tool_call_id)
        if msg_tool_calls := message.get("tool_calls"):
            sdk_message["tool_calls"] = cast(list, msg_tool_calls)
        if msg_graph_data := message.get("graph_data"):
            sdk_message["graph_data"] = cast(
                GraphData,
                msg_graph_data
                )
        if msg_refusal := message.get("refusal"):
            sdk_message["refusal"] = cast(str, msg_refusal)
        return sdk_message

    def _register_callable(
            self,
            callable_to_register: Callable,
            name: str,
            parameters: Dict[str, FunctionToolParameterMeta]
    ):
        """
        Internal helper function to store a provided callable
        for function call, to retrieve it when processing LLM response
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
        """
        Clear ongoing tool calls after they've been processed
        """
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
            index: ongoing_tool_call.get(
                "res",
                {
                    "role": "tool",
                    "content": "ERROR: Failed to get function call result – " +
                    "the function was never called. The most likely reason " +
                    "is LLM never issuing a `finish_reason: 'tool_calls'`. " +
                    "Please DO NOT RETRY the function call and inform " +
                    "the user about the error."
                }
            )
            for index, ongoing_tool_call
            in self._ongoing_tool_calls.items()
            }

    def _gather_tool_calls_results(self):
        return list(self._gather_tool_calls_messages().values())

    def _prepare_tool(
            self,
            tool_instance: Union['Graph', GraphTool, FunctionTool, LLMTool]
            ) -> Union[SDKGraphTool, SDKFunctionTool, SDKLlmTool]:
        """
        Internal helper function to process a tool instance
        into the required format.
        """
        def validate_parameters(
                parameters: Dict[str, FunctionToolParameterMeta]
        ) -> bool:
            """
            Validates the `parameters` dictionary to ensure that each key
            is a parameter name, and each value is a dictionary containing
            at least a `type` field, and optionally a `description`.

            :param parameters: The parameters dictionary to validate.
            :return: True if valid, raises ValueError if invalid.
            """
            if not isinstance(parameters, dict):
                raise ValueError("`parameters` must be a dictionary")

            for param_name, param_info in parameters.items():
                if not isinstance(param_info, dict):
                    raise ValueError(
                        f"Parameter '{param_name}' must be a dictionary"
                        )

                if "type" not in param_info:
                    raise ValueError(
                        f"Parameter '{param_name}' must include a 'type' field"
                        )

                if not isinstance(param_info["type"], str):
                    raise ValueError(
                        f"'type' for parameter '{param_name}' must be a string"
                        )

                supported_types = {
                    "string", "number", "integer", "float",
                    "boolean", "array", "object", "null"
                }
                if param_info["type"] not in supported_types:
                    logging.warning(
                        f"Unsupported type '{param_info['type']}' " +
                        f"for parameter '{param_name}'. " +
                        "Fallback to 'string' type will be used. " +
                        "This may lead to unexpected results. " +
                        f"Supported types are: {supported_types}"
                    )

                # Optional 'description' validation (if provided)
                if (
                    "description" in param_info
                    and
                    not isinstance(param_info["description"], str)
                ):
                    raise ValueError(
                        f"'description' for parameter '{param_name}' " +
                        "must be a string if provided"
                        )

            return True

        def prepare_parameters(
                parameters: Dict[str, FunctionToolParameterMeta]
        ) -> Dict:
            """
            Prepares the parameters dictionary for a function tool.

            :param parameters: The parameters dictionary to prepare.
            :return: The processed parameters dictionary.
            """
            processed_params: Dict[str, FunctionToolParameterMeta] = {}
            if not parameters:
                return processed_params
            else:
                required_list = []
                for param_name, param_info in parameters.items():
                    processed_param = param_info.copy()
                    # Convert Python numeric types to JSON schema "number" type
                    if processed_param["type"] in ["float", "integer"]:
                        processed_param["type"] = "number"
                    # Check the "required" flag on parameter
                    if processed_param.get("required", False) is True:
                        required_list.append(param_name)
                    processed_params[param_name] = processed_param

            res = {
                "type": "object",
                "properties": processed_params
            }
            if required_list:
                res["required"] = required_list
            return res

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
                        "subqueries": True,
                        "description": tool_instance.description
                    }
                }
            )

        elif isinstance(tool_instance, dict):
            # Handle a dictionary (either a graph, a function or a LLM tool)
            if "type" not in tool_instance:
                raise ValueError(
                    "Invalid tool definition: 'type' field is missing"
                    )

            tool_type = tool_instance["type"]

            if tool_type == "graph":
                tool_instance = cast(GraphTool, tool_instance)
                if "graph_ids" not in tool_instance:
                    raise ValueError("Graph tool must include 'graph_ids'")
                if "description" not in tool_instance:
                    logging.warning(
                        "No description provided for `graph` tool. " +
                        "This may produce suboptimal results. " +
                        "To increase output quality, provide a description " +
                        "for the tool."
                        )
                # Return graph tool JSON

                graph_ids_valid = \
                    validate_graph_ids(tool_instance["graph_ids"])
                if graph_ids_valid:
                    return cast(
                        SDKGraphTool,
                        {
                            "type": "graph",
                            "function": {
                                "graph_ids": tool_instance["graph_ids"],
                                "subqueries": tool_instance.get(
                                    "subqueries", False
                                    ),
                                "description": tool_instance.get(
                                    "description", None
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
                if (
                    "name" not in tool_instance
                    or
                    "parameters" not in tool_instance
                ):
                    raise ValueError(
                        "Function tool must include 'name' and 'parameters'"
                        )
                if "description" not in tool_instance:
                    logging.warning(
                        "No description provided for `function` tool. " +
                        "This may produce suboptimal results. " +
                        "To increase output quality, provide a description " +
                        "for the tool."
                        )

                parameters_valid = \
                    validate_parameters(tool_instance["parameters"])
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
                                "parameters":
                                    prepare_parameters(
                                        tool_instance["parameters"]
                                        ),
                                "description": tool_instance.get("description")
                                }
                        }
                    )
                else:
                    raise ValueError(
                        "Invalid parameters for function " +
                        f"`{tool_instance['name']}`"
                        )

            elif tool_type == "llm":
                tool_instance = cast(LLMTool, tool_instance)
                if "model" not in tool_instance:
                    raise ValueError("LLM tool must include 'model'")
                if "description" not in tool_instance:
                    logging.warning(
                        "No description provided for `llm` tool. " +
                        "This may produce suboptimal results. " +
                        "To increase output quality, provide a description " +
                        "for the tool."
                        )
                # Return LLM tool JSON
                return cast(
                    SDKLlmTool,
                    {
                        "type": "llm",
                        "function": {
                            "model": tool_instance["model"],
                            "description": tool_instance.get("description")
                        }
                    }
                )
            else:
                raise ValueError(f"Unsupported tool type: {tool_type}")

        else:
            raise ValueError(f"Invalid tool input: {tool_instance}")

    def __add__(self, chunk_or_message: Union['Conversation.Message', dict]):
        """
        Adds a message or appends a chunk to the last message
        in the conversation.

        :param chunk_or_message: Dictionary representation of a message
        or chunk to add.
        :raises TypeError: If passed chunk_or_message is not a dictionary.
        :raises ValueError: If chunk_or_message is not a proper message
        with "role" and "content".
        """
        if not isinstance(chunk_or_message, dict):
            raise TypeError(
                "Conversation only supports dict operands for addition"
                )
        if chunk_or_message.get("chunk") is True:
            chunk = chunk_or_message
            self._merge_chunk_to_last_message(cast(dict, chunk))
        else:
            message = chunk_or_message
            self.validate_message(message)
            message_to_append = {
                "role": message["role"],
                "content": message["content"],
                "actions": message.get("actions")
                }
            if "tool_calls" in message:
                message_to_append["tool_calls"] = message["tool_calls"]
            if "tool_call_id" in message and message["role"] == "tool":
                message_to_append["tool_call_id"] = message["tool_call_id"]
            self.messages.append(cast(Conversation.Message, message_to_append))
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
            request_model: str,
            request_data: ChatOptions,
            stream: bool = False
    ) -> Union[Stream, ChatCompletion]:
        """
        Helper function to send a chat request to the LLM.

        :param request_model: Model to use for the chat.
        :param request_data: Configuration settings for the chat request.
        :param stream: Whether to use streaming mode.
        :return: The response from the LLM, either as
        a Stream or a ChatCompletion object.
        """
        client = WriterAIManager.acquire_client()
        prepared_messages = [
                self._prepare_message(message)
                for message in self.messages
            ]
        logging.debug(
            "Attempting to request a message from LLM: " +
            f"prepared messages – {prepared_messages}, " +
            f"request_data – {request_data}"
            )
        return client.chat.chat(
            messages=prepared_messages,
            model=request_model,
            stream=stream,
            logprobs=request_data.get('logprobs', NotGiven()),
            tools=request_data.get('tools', NotGiven()),
            tool_choice=request_data.get('tool_choice', NotGiven()),
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
        :raises ValueError: If the value cannot be converted
        to the target type.
        """
        if target_type == "string":
            return str(value)
        elif target_type == "number":
            return float(value)  # as float is more specific
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
        elif target_type == "null":
            return None
        else:
            logging.warning(
                f"Unsupported target type: {target_type}. " +
                "Falling back to string type. " +
                "This may lead to unexpected results.")
            return str(value)

    def _check_if_arguments_are_required(self, function_name: str) -> bool:
        callable_entry = self._callable_registry.get(function_name)
        if not callable_entry:
            raise RuntimeError(
                f"Tried to check arguments of function {function_name} " +
                "which is not present in the conversation's callable registry."
                )
        callable_parameters = callable_entry.get("parameters")
        return \
            callable_parameters is not None \
            and \
            callable_parameters != {}

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
            if (
                not arguments
                and
                not self._check_if_arguments_are_required(function_name)
            ):
                parsed_arguments = {}
            else:
                parsed_arguments = json.loads(arguments)
            callable_entry = self._callable_registry.get(function_name)

            if callable_entry:
                param_specs = callable_entry["parameters"]
                # Convert arguments based on registered parameter types
                converted_arguments = {}
                try:
                    for param_name, param_info in param_specs.items():
                        if param_name in parsed_arguments:
                            target_type = param_info["type"]
                            value = parsed_arguments[param_name]
                            converted_arguments[param_name] = \
                                self._convert_argument_to_type(
                                    value,
                                    target_type
                                    )
                        elif param_info.get("required") is True:
                            raise ValueError(
                                f"Missing required parameter: {param_name}"
                                )

                    func = callable_entry.get("callable")
                    if not func:
                        raise ValueError(
                            f"Misconfigured function {function_name}: " +
                            "no callable provided"
                            )

                    # Call the function with converted arguments
                    func_result = func(**converted_arguments)
                except Exception as e:
                    logging.error(
                        "An error occured during the execution of function " +
                        f"`{function_name}`: {e}"
                    )
                    func_result = \
                        "Function call failed due to an exception – " + \
                        "please DO NOT RETRY the call and inform the user " + \
                        "about the error"

                # Prepare follow-up message with the function call result
                follow_up_message = {
                    "role": "tool",
                    "name": function_name,
                    "tool_call_id": tool_call_id,
                    "content": f"{func_result}"
                }

                return follow_up_message
            else:
                raise ValueError(
                    f"`{function_name}` is not present in callable registry"
                    )

        except json.JSONDecodeError:
            logging.error(
                f"Failed to parse arguments for tool call: {arguments}"
                )

        return {
                    "role": "tool",
                    "name": function_name,
                    "tool_call_id": tool_call_id,
                    "content":
                            "Failed to parse provided arguments " +
                            "for tool call – please DO NOT RETRY " +
                            "the function call and inform the user " +
                            "about the error."
                }

    def _process_tool_call(
            self,
            index,
            tool_call_id,
            tool_call_name,
            tool_call_arguments
            ):
        if index not in self._ongoing_tool_calls:
            self._ongoing_tool_calls[index] = {
                "name": None,
                "arguments": "",
                "tool_call_id": None
            }

        # Capture `tool_call_id` from the message
        if tool_call_id is not None and tool_call_id != '':
            self._ongoing_tool_calls[index]["tool_call_id"] = tool_call_id

        # Capture `name` for function call
        if tool_call_name is not None and tool_call_name != '':
            self._ongoing_tool_calls[index]["name"] = tool_call_name

        # Accumulate arguments across chunks
        if tool_call_arguments is not None and tool_call_arguments != '':
            self._ongoing_tool_calls[index]["arguments"] += \
                tool_call_arguments

        # Check if we have all necessary data to execute the function
        tool_call_id, tool_call_name, tool_call_arguments = \
            self._ongoing_tool_calls[index]["tool_call_id"], \
            self._ongoing_tool_calls[index]["name"], \
            self._ongoing_tool_calls[index]["arguments"]

        tool_call_id_ready = \
            tool_call_id is not None \
            and tool_call_id != ''
        tool_call_name_ready = \
            tool_call_name is not None \
            and tool_call_name != ''

        # Check whether the arguments are prepared properly -
        # either present in correct format
        # or should not be used due to not being required for the function
        if tool_call_name_ready:
            # Function name is needed to check the function for params
            tool_call_arguments_not_required = \
                (
                    not tool_call_arguments
                    and
                    not self._check_if_arguments_are_required(
                        tool_call_name
                    )
                )
            tool_call_arguments_formatted_properly = \
                (
                    isinstance(
                        tool_call_arguments, str
                    )
                    and
                    tool_call_arguments.endswith("}")
                )
            tool_call_arguments_ready = \
                tool_call_arguments_not_required \
                or \
                tool_call_arguments_formatted_properly
        else:
            tool_call_arguments_ready = False

        if (
            tool_call_id_ready
            and
            tool_call_name_ready
            and
            tool_call_arguments_ready
        ):
            follow_up_message = self._execute_function_tool_call(index)
            if follow_up_message:
                self._ongoing_tool_calls[index]["res"] = follow_up_message

    def _process_tool_calls(self, message: ChatCompletionMessage):
        if message.tool_calls:
            for helper_index, tool_call in enumerate(message.tool_calls):
                index = tool_call.index or helper_index
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
            for helper_index, tool_call in enumerate(tool_calls):
                index = tool_call["index"] or helper_index
                tool_call_id = tool_call["id"]
                tool_call_name = tool_call["function"]["name"]
                tool_call_arguments = tool_call["function"]["arguments"]

                self._process_tool_call(
                    index,
                    tool_call_id,
                    tool_call_name,
                    tool_call_arguments
                )

    def _prepare_received_message_for_history(
            self,
            message: ChatCompletionMessage
            ):
        """
        Prepares a received message for adding to the conversation history.

        :param message: The message to prepare.
        :return: The prepared message.
        """
        raw_message = message.model_dump()
        if not raw_message.get("content"):
            raw_message["content"] = ""
        return raw_message

    def _process_response_data(
            self,
            response_data: ChatCompletion,
            request_model: str,
            request_data: ChatOptions,
            depth=1,
            max_depth=5
            ) -> 'Conversation.Message':
        if depth > max_depth:
            raise RuntimeError(
                "Reached maximum depth " +
                "when processing response data tool calls."
                )
        for entry in response_data.choices:
            message = entry.message
            if message:
                # Handling tool call fragments
                logging.debug(f"Received message – {message}")
                if message.tool_calls is not None:
                    logging.debug(
                        f"Message has tool calls - {message.tool_calls}"
                        )
                    self += self._prepare_received_message_for_history(message)
                    self._process_tool_calls(message)
                    self.messages += self._gather_tool_calls_results()
                    # Send follow-up call to LLM
                    logging.debug("Sending a request to LLM")
                    follow_up_response = cast(
                        ChatCompletion,
                        self._send_chat_request(
                            request_model=request_model,
                            request_data=request_data
                        )
                    )
                    logging.debug(f"Received response – {follow_up_response}")

                    # Call the function recursively
                    # to either process a new tool call
                    # or return the message if no tool calls are requested

                    self._clear_ongoing_tool_calls()
                    return self._process_response_data(
                        follow_up_response,
                        request_model=request_model,
                        request_data=request_data,
                        depth=depth+1
                        )
                else:
                    return cast(Conversation.Message, message.model_dump())
        raise RuntimeError(
            "Failed to acquire proper response " +
            f"for completion from data: {response_data}"
            )

    def _process_stream_response(
            self,
            response: Stream,
            request_model: str,
            request_data: ChatOptions,
            depth=1,
            max_depth=5,
            flag_chunks=False
    ) -> Generator[dict, None, None]:
        if depth > max_depth:
            raise RuntimeError(
                "Reached maximum depth " +
                "when processing response data tool calls."
                )

        for line in response:
            chunk_data, chunk = _process_chat_data_chunk(line)

            if flag_chunks is True:
                # We avoid flagging first chunk
                # to trigger creating a message
                # to append chunks to
                chunk |= {"chunk": True}

            # Handling tool call fragments
            tool_calls_present = chunk.get("tool_calls") is not None
            tool_calls_need_processing = \
                chunk_data.get("finish_reason") == "tool_calls"
            if tool_calls_present or tool_calls_need_processing:
                # Handle tool calls chunks
                if tool_calls_present:
                    self += chunk
                    self._process_streaming_tool_calls(chunk)
                if tool_calls_need_processing:
                    # Send follow-up call to LLM
                    self.messages += self._gather_tool_calls_results()
                    follow_up_response = cast(
                        Stream,
                        self._send_chat_request(
                            request_model=request_model,
                            request_data=request_data,
                            stream=True
                        )
                    )

                    try:
                        self._clear_ongoing_tool_calls()
                        yield from self._process_stream_response(
                            response=follow_up_response,
                            request_model=request_model,
                            request_data=request_data,
                            depth=depth+1,
                            max_depth=max_depth,
                            flag_chunks=False
                        )
                    finally:
                        follow_up_response.close()
            else:
                # Handle regular message chunks
                if chunk.get("content") is not None:
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
                    LLMTool,
                    List[Union[Graph, GraphTool, FunctionTool, LLMTool]]
                    ]  # can be an instance of tool or a list of instances
                ] = None,
            max_tool_depth: int = 5,
            ) -> 'Conversation.Message':
        """
        Processes the conversation with the current messages and additional
        data to generate a response.
        Note: this method only produces AI model output and does not attach the
        result to the existing conversation history.

        :param tools: Optional tools to use for processing.
        :param config: Optional parameters to pass for processing.
        :param max_tool_depth: Maximum depth for tool calls processing.
        :return: Generated message.
        :raises RuntimeError: If response data was not properly formatted
        to retrieve model text.
        """
        config = config or {'max_tokens': 1024}
        if tools is not None and not isinstance(tools, list):
            tools = [tools]

        prepared_tools = [
            self._prepare_tool(tool_instance)
            for tool_instance in (tools or [])
            ]

        request_data: ChatOptions = {**config, **self.config}
        if prepared_tools:
            request_data |= {"tools": prepared_tools}
        request_model = \
            request_data.get("model") or WriterAIManager.use_chat_model()

        response_data: ChatCompletion = cast(
                ChatCompletion,
                self._send_chat_request(
                    request_model=request_model,
                    request_data=request_data
                )
            )

        response = self._process_response_data(
            response_data,
            request_model=request_model,
            request_data=request_data,
            max_depth=max_tool_depth
            )

        # Clear buffer and callable registry for the completed tool call
        self._clear_tool_calls_helpers()

        return response

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
                ] = None,
            max_tool_depth: int = 5
            ) -> Generator[dict, None, None]:
        """
        Initiates a stream to receive chunks of the model's reply.
        Note: this method only produces AI model output and does not attach
        the result to the existing conversation history.

        :param tools: Optional tools to use for processing.
        :param config: Optional parameters to pass for processing.
        :param max_tool_depth: Maximum depth for tool calls processing.
        :yields: Model response chunks as they arrive from the stream.
        """
        config = config or {}
        if tools is not None and not isinstance(tools, list):
            tools = [tools]

        prepared_tools = [
            self._prepare_tool(tool_instance)
            for tool_instance in (tools or [])
            ]

        request_data: ChatOptions = {**config, **self.config}
        if prepared_tools:
            request_data |= {"tools": prepared_tools}
        request_model = \
            request_data.get("model") or WriterAIManager.use_chat_model()

        response: Stream = cast(
            Stream,
            self._send_chat_request(
                request_model=request_model,
                request_data=request_data,
                stream=True
            )
        )

        yield from self._process_stream_response(
            response=response,
            request_model=request_model,
            request_data=request_data,
            max_depth=max_tool_depth
        )

        # Clear buffer and callable registry for the completed tool call
        self._clear_tool_calls_helpers()
        response.close()

    def _is_serialized(self, message: 'Conversation.Message') -> bool:
        """
        Function to verify whether the message should be serializable.

        :return: Boolean indicating if the message meets
        the criteria for serialization.
        """
        if message["role"] in ["system", "tool"]:
            # Prevent serialization of messages
            # not intended for user display
            return False
        elif not message.get("content"):
            # Prevent serialization for messages
            # without meaningful content
            return False

        return True

    def _serialize_message(self, message: 'Conversation.Message'):
        return {
            "role": message["role"],
            "content": message["content"],
            "actions": message["actions"]
            }

    @property
    def serialized_messages(self) -> List['Conversation.Message']:
        """
        Returns a representation of the conversation, excluding system
        messages.

        :return: List of messages without system messages.
        """
        # Excluding system messages for privacy & security reasons
        serialized_messages = \
            [
                self._serialize_message(message)
                for message in self.messages
                if self._is_serialized(message)
            ]
        return serialized_messages


class Apps:
    def list(
            self,
            config: Optional[APIOptions] = None
            ) -> List[ApplicationListResponse]:
        """
        Lists all applications available to the user.

        :param config: Optional dictionary containing parameters
        for the list call.
        :return: List of applications.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.
        """
        client = WriterAIManager.acquire_client()
        config = config or {}

        response = client.applications.list(**config)
        # Convert the response to list
        # to collect all the apps available
        result = list(response)

        return result

    def retrieve(
            self,
            application_id: str,
            config: Optional[APIOptions] = None
            ) -> ApplicationRetrieveResponse:
        """
        Retrieves all information about a specific application by its ID.

        :param application_id: The ID of the application to retrieve data for.
        :param config: Optional dictionary containing parameters
        for the retrieve call.
        :return: The application data.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.
        """
        client = WriterAIManager.acquire_client()
        config = config or {}

        response_data = client.applications.retrieve(
            application_id=application_id,
            **config
            )
        return response_data

    def generate_content(
            self,
            application_id: str,
            input_dict: Optional[Dict[str, str]] = None,
            async_job: Optional[bool] = False,
            config: Optional[APIOptions] = None
            ) -> Union[str, JobCreateResponse]:
        """
        Generates output based on an existing AI Studio no-code application.

        :param application_id: The id for the application, which can be
            obtained on AI Studio.
        :param input_dict: Optional dictionary containing parameters for
            the generation call.
        :param async_job: Optional. If True, the function initiates
            an asynchronous job and returns job details instead of
            waiting for the immediate output.
        :return: The generated text
            or the information about new asynchronous job.
        :raises RuntimeError: If response data was not properly formatted
        to retrieve model text.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.

        Examples:

        **Synchronous Call (Immediate Output)**

        >>> response = writer.ai.apps.generate_content(
        ...     application_id="app_123",
        ...     input_dict={"topic": "Climate Change"},
        ...     async_job=False
        ... )
        >>> print(response)
        "Climate change refers to long-term shifts in temperatures and weather patterns..."

        **Asynchronous Call (Job Creation)**

        >>> response = writer.ai.apps.generate_content(
        ...     application_id="app_123",
        ...     input_dict={"topic": "Climate Change"},
        ...     async_job=True
        ... )
        >>> print(response)
        JobCreateResponse(id="job_456", created_at=datetime(2025, 2, 24, 12, 30, 45), status="in_progress")
        >>> result = writer.ai.apps.retrieve_job(job_id=response.id)
        >>> if result.status == "completed":
        ...     print(result.data)
        {"title": "output", "suggestion": "Climate change refers to long-term shifts in temperatures and weather patterns..."}

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

        if not async_job:
            response_data = client.applications.generate_content(
                application_id=application_id,
                inputs=inputs,
                **config
                )

            text = response_data.suggestion
            if text:
                return text

            raise RuntimeError(
                "Failed to acquire proper response " +
                "for completion from data: " +
                f"{response_data}"
            )

        else:
            async_response_data = client.applications.jobs.create(
                application_id=application_id,
                inputs=inputs,
                **config
            )

            return async_response_data

    def retry_job(
            self,
            job_id: str,
            config: Optional[APIOptions] = None
            ) -> JobRetryResponse:
        """
        Retries a specific asynchronous job execution.

        :param job_id: The unique identifier of the job to retry.
        :param config: Optional API configuration options for
        the retry request.
        :return: The response data from retrying the job.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.
        """
        client = WriterAIManager.acquire_client()
        config = config or {}

        response_data = client.applications.jobs.retry(
            job_id=job_id,
            **config
            )

        return response_data

    def retrieve_jobs(
            self,
            application_id: str,
            config: Optional[APIRetrieveJobsOptions] = None
            ) -> List[ApplicationGenerateAsyncResponse]:
        """
        Retrieves a list of jobs for a specific application.

        :param application_id: The unique identifier of the application.
        :param config: Optional configuration parameters for the API request.
        :return: A list of job responses associated with
        the specified application.

        The `config` dictionary can include:
        - `limit` (int): The pagination limit for retrieving the jobs.
        - `offset` (int): The pagination offset for retrieving the jobs.
        - `status` (Literal['in_progress', 'failed', 'completed']):
        Filter jobs by the provided status.
        - `extra_headers` (Optional[Headers]): Additional headers.
        - `extra_query` (Optional[Query]): Extra query parameters.
        - `extra_body` (Optional[Body]): Additional body data.
        - `timeout` (Union[float, Timeout, None, NotGiven]):
        Request timeout in seconds.
        """
        client = WriterAIManager.acquire_client()
        config = config or {}

        jobs = client.applications.jobs.list(
            application_id=application_id,
            **config
        )

        return list(jobs)

    def retrieve_job(
            self,
            job_id: str,
            config: Optional[APIOptions] = None
            ) -> ApplicationGenerateAsyncResponse:
        """
        Retrieves an asynchronous job from the Writer AI API based on its ID.

        :param job_id: The unique identifier of the job to retrieve.
        :param config: Additional API configuration options.
        :returns: The retrieved job object from the API.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.
        """
        client = WriterAIManager.acquire_client()
        config = config or {}

        job = client.applications.jobs.retrieve(
            job_id=job_id,
            **config
        )

        return job

    def retrieve_graphs(
            self,
            application_id: str,
            config: Optional[APIOptions] = None
            ) -> List[str]:
        """
        Retrieves a list of graph IDs for a specific application.

        :param application_id: The unique identifier of the application.
        :param config: Optional configuration parameters for the API request.
        :return: A list of graph IDs associated with the specified application.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.
        """
        client = WriterAIManager.acquire_client()
        config = config or {}

        graphs = client.applications.graphs.list(
            application_id=application_id,
            **config
        )

        return graphs.graph_ids

    def associate_graphs(
            self,
            application_id: str,
            graph_ids: List[str],
            config: Optional[APIOptions] = None
            ) -> ApplicationGraphsResponse:
        """
        Associates a list of graph IDs with a specific application.

        :param application_id: The unique identifier of the application.
        :param graph_ids: A list of graph IDs to associate with
        the application.
        :param config: Optional configuration parameters for the API request.
        :return: The response data from associating the graphs.

        The `config` dictionary can include the following keys:
        - `extra_headers` (Optional[Headers]):
        Additional headers for the request.
        - `extra_query` (Optional[Query]):
        Additional query parameters for the request.
        - `extra_body` (Optional[Body]):
        Additional body parameters for the request.
        - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
        Timeout for the request in seconds.
        """
        client = WriterAIManager.acquire_client()
        config = config or {}

        response_data = client.applications.graphs.update(
            application_id=application_id,
            graph_ids=graph_ids,
            **config
            )

        return response_data


class Tools:
    SplittingStrategy = Union[
        Literal["llm_split"],
        Literal["fast_split"],
        Literal["hybrid_split"]
        ]
    MedicalResponseType = Union[
        Literal["Entities"],
        Literal["RxNorm"],
        Literal["ICD-10-CM"],
        Literal["SNOMED CT"]
    ]

    @staticmethod
    def _retrieve_tools_accessor():
        return WriterAIManager.acquire_client().tools

    @classmethod
    def parse_pdf(
        cls,
        file_id_or_file: Union[str, File, Dict],
        format: Union[Literal['text'], Literal['markdown']] = 'text',
        config: Optional[APIOptions] = None
    ) -> str:
        config = config or {}
        client_tools = cls._retrieve_tools_accessor()
        file_id = None
        if isinstance(file_id_or_file, File):
            file_id = file_id_or_file.id
        elif isinstance(file_id_or_file, Dict):
            if not (
                "data" in file_id_or_file
                and
                "type" in file_id_or_file
                and
                "name" in file_id_or_file
            ):
                raise ValueError(
                    "Invalid payload passed to parse_pdf method: " +
                    "expected keys `data`, `type` and `name`, " +
                    f"got {file_id_or_file.keys()}"
                    )
            new_file_from_payload = upload_file(
                **file_id_or_file,
                config=config
                )
            file_id = new_file_from_payload.id
        elif isinstance(file_id_or_file, str):
            file_id = file_id_or_file
        else:
            raise ValueError(
                "parse_pdf expects a `writer.ai.File` type instance, " +
                f"a file payload, or a string ID: got {type(file_id_or_file)}"
            )

        result = client_tools.parse_pdf(
            file_id=file_id,
            format=format,
            **config
        )

        return result.content

    @classmethod
    def split(
        cls,
        content: str,
        strategy: SplittingStrategy = "llm_split",
        config: Optional[APIOptions] = None
    ) -> List[str]:
        if not content:
            raise ValueError("Content cannot be empty.")
        config = config or {}
        client_tools = cls._retrieve_tools_accessor()

        result = client_tools.context_aware_splitting(
            strategy=strategy,
            text=content,
            **config
        )

        return result.chunks

    @classmethod
    def comprehend_medical(
        cls,
        content: str,
        response_type: MedicalResponseType = "Entities",
        config: Optional[APIOptions] = None
    ) -> List:
        if not content:
            raise ValueError("Content cannot be empty.")
        config = config or {}
        client_tools = cls._retrieve_tools_accessor()

        result = client_tools.comprehend.medical(
            content=content,
            response_type=response_type,
            **config
        )

        return result.entities


def complete(
        initial_text: str,
        config: Optional['CreateOptions'] = None
        ) -> str:
    """
    Completes the input text using the given data and returns the first
    resulting text choice.

    :param initial_text: The initial text prompt for the completion.
    :param config: Optional dictionary containing parameters
    for the completion call.
    :return: The text of the first choice from the completion response.
    :raises RuntimeError: If response data was not properly formatted
    to retrieve model text.
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
    Streams completion results from an initial text prompt, yielding
    each piece of text as it is received.

    :param initial_text: The initial text prompt for the stream completion.
    :param config: Optional dictionary containing parameters
    for the stream completion call.
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


def _gather_graph_ids(graphs_or_graph_ids: list) -> List[str]:
    graph_ids = []
    for item in graphs_or_graph_ids:
        if isinstance(item, Graph):
            graph_ids.append(item.id)
        elif isinstance(item, str):
            graph_ids.append(item)
        else:
            raise ValueError(
                f"Invalid item in graphs_or_graph_ids list: {type(item)}"
                )

    return graph_ids


def ask(
    question: str,
    graphs_or_graph_ids: List[Union[Graph, str]],
    subqueries: bool = False,
    config: Optional[APIOptions] = None
):
    """
    Sends a question to the specified graph(s) and retrieves
    a single response.

    :param question: The query or question to be answered by the graph(s).
    :param graphs_or_graph_ids: A list of `Graph` objects or graph IDs that
    should be queried.
    :param subqueries: Enables subquery generation if set to True,
    enhancing the result.
    :param config: Optional dictionary for additional API
    configuration settings.

    :return: The answer to the question from the graph(s).

    :raises ValueError: If an invalid graph or graph ID is provided
    in `graphs_or_graph_ids`.
    :raises RuntimeError: If the API response is improperly formatted
    or the answer cannot be retrieved.

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.

    **Example Usage**:

    >>> response = ask(
    ...     question="What is the capital of France?",
    ...     graphs_or_graph_ids=["graph_id_1", "graph_id_2"]
    ... )
    """
    config = config or {}
    client = WriterAIManager.acquire_client()
    graph_ids = _gather_graph_ids(graphs_or_graph_ids)

    response = cast(
        Question,
        client.graphs.question(
            graph_ids=graph_ids,
            question=question,
            stream=False,
            subqueries=subqueries,
            **config
        )
    )

    return response.answer


def stream_ask(
    question: str,
    graphs_or_graph_ids: List[Union[Graph, str]],
    subqueries: bool = False,
    config: Optional[APIOptions] = None
) -> Generator[str, None, None]:
    """
    Streams response for a question posed to the specified graph(s).

    This method returns incremental chunks of the response, ideal for long
    responses or when reduced latency is needed.

    :param question: The query or question to be answered by the graph(s).
    :param graphs_or_graph_ids: A list of Graph objects or graph IDs that
    should be queried.
    :param subqueries: Enables subquery generation if set to True,
    enhancing the result.
    :param config: Optional dictionary for additional API
    configuration settings.

    :yields: Incremental chunks of the answer to the question.

    :raises ValueError: If an invalid graph or graph ID
    is provided in `graphs_or_graph_ids`.

    The `config` dictionary can include the following keys:
    - `extra_headers` (Optional[Headers]):
    Additional headers for the request.
    - `extra_query` (Optional[Query]):
    Additional query parameters for the request.
    - `extra_body` (Optional[Body]):
    Additional body parameters for the request.
    - `timeout` (Union[float, httpx.Timeout, None, NotGiven]):
    Timeout for the request in seconds.

    **Example Usage**:

    >>> for chunk in stream_ask(
    ...     question="What are the benefits of renewable energy?",
    ...     graphs_or_graph_ids=["graph_id_1"]
    ... ):
    ...     print(chunk)
    ...
    """
    config = config or {}
    client = WriterAIManager.acquire_client()
    graph_ids = _gather_graph_ids(graphs_or_graph_ids)

    response = cast(
        Stream[QuestionResponseChunk],
        client.graphs.question(
            graph_ids=graph_ids,
            question=question,
            stream=True,
            subqueries=subqueries,
            **config
        )
    )

    for chunk in response._iter_events():
        raw_data = chunk.data
        answer = ""
        try:
            data = json.loads(raw_data)
            answer = data.get("answer", "")
        except json.JSONDecodeError:
            logging.error(
                "Couldn't parse chunk data during `question` streaming"
                )
        yield answer


def init(token: Optional[str] = None):
    """
    Initializes the WriterAIManager with an optional token.

    :param token: Optional token for authentication.
    :return: An instance of WriterAIManager.
    """
    return WriterAIManager(token=token)


apps = Apps()
tools = Tools()
