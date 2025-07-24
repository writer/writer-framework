from typing import Any, Dict, List, Optional, Protocol, Tuple, Union

from pydantic import BaseModel
from typing_extensions import Literal, TypedDict


class WriterFileItem(TypedDict):
    name: str
    type: str
    data: str


class InstancePathItem(TypedDict):
    componentId: str
    instanceNumber: int


InstancePath = List[InstancePathItem]


class Readable(Protocol):
    def read(self) -> Any: ...


ServeMode = Literal["run", "edit"]
MessageType = Literal[
    "sessionInit",
    "componentUpdate",
    "event",
    "codeUpdate",
    "codeSave",
    "checkSession",
    "keepAlive",
    "stateEnquiry",
    "setUserinfo",
    "stateContent",
    "hashRequest",
    "listResources",
    "writerVaultUpdate",
    "queueMessage",
    "retrieveMessages",
    "clearMessages"
]


class AbstractTemplate(BaseModel):
    baseType: str
    writer: Dict


class SourceFilesFile(TypedDict):
    type: Literal["file"]
    complete: Optional[bool]
    content: str


class SourceFilesBinary(TypedDict):
    type: Literal["binary"]


class SourceFilesDirectory(TypedDict):
    type: Literal["directory"]
    children: Dict[str, "SourceFiles"]


SourceFiles = Union[SourceFilesFile, SourceFilesDirectory, SourceFilesBinary]

# Web server models


class WriterApplicationInformation(BaseModel):
    id: str
    organizationId: str
    baseUrl: Optional[str] = None
    apiKey: Optional[str] = None


class AutogenRequestBody(BaseModel):
    description: str


class InitRequestBody(BaseModel):
    proposedSessionId: Optional[str] = None


class InitResponseBody(BaseModel):
    mode: Literal["run", "edit"]
    sessionId: str
    userState: Dict
    mail: List
    components: Dict
    userFunctions: List[Dict]
    extensionPaths: List
    featureFlags: List[str]
    abstractTemplates: Dict[str, AbstractTemplate]
    writerApplication: Optional[WriterApplicationInformation]


class InitResponseBodyRun(InitResponseBody):
    mode: Literal["run"]


class InitResponseBodyEdit(InitResponseBody):
    mode: Literal["edit"]
    runCode: Optional[str] = None
    sourceFiles: SourceFilesDirectory = {"type": "directory", "children": {}}


class WriterWebsocketIncoming(BaseModel):
    type: str
    trackingId: int
    payload: Dict[str, Any]


class WriterWebsocketOutgoing(BaseModel):
    messageType: str
    trackingId: int
    payload: Optional[Dict[str, Any]] = None


# AppProcessServer Requests


class AppProcessServerRequest(BaseModel):
    type: MessageType
    payload: Optional[Any] = None


class InitSessionRequestPayload(BaseModel):
    cookies: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    proposedSessionId: Optional[str] = None


class InitSessionRequest(AppProcessServerRequest):
    type: Literal["sessionInit"]
    payload: InitSessionRequestPayload


class ComponentUpdateRequestPayload(BaseModel):
    components: Dict


class ComponentUpdateRequest(AppProcessServerRequest):
    type: Literal["componentUpdate"]
    payload: ComponentUpdateRequestPayload


class ListResourcesRequestPayload(BaseModel):
    resource_type: str


class ListResourcesRequest(AppProcessServerRequest):
    type: Literal["listResources"]
    payload: ListResourcesRequestPayload


class WriterVaultUpdateRequest(AppProcessServerRequest):
    type: Literal["writerVaultUpdate"]


class WriterEvent(BaseModel):
    type: str
    isSafe: Optional[bool] = False
    handler: Optional[str] = None
    instancePath: Optional[InstancePath] = None
    payload: Optional[Any] = None


class EventRequest(AppProcessServerRequest):
    type: Literal["event"]
    payload: WriterEvent


class StateEnquiryRequest(AppProcessServerRequest):
    type: Literal["stateEnquiry"]


class StateContentRequest(AppProcessServerRequest):
    type: Literal["stateContent"]


class HashRequestPayload(BaseModel):
    message: str


class HashRequest(AppProcessServerRequest):
    type: Literal["hashRequest"]
    payload: HashRequestPayload


class QueueMessageRequest(AppProcessServerRequest):
    type: Literal["queueMessage"]
    payload: Any

AppProcessServerRequestPacket = Tuple[int, str, AppProcessServerRequest]

# AppProcessServer Responses


class AppProcessServerResponse(BaseModel):
    status: Literal["ok", "error"]
    status_message: Optional[str] = None
    payload: Optional[Any] = None


class InitSessionResponsePayload(BaseModel):
    sessionId: str
    userState: Dict[str, Any]
    mail: List
    userFunctions: List[Dict]
    components: Dict
    featureFlags: List[str]
    writerApplication: Optional[WriterApplicationInformation]


class InitSessionResponse(AppProcessServerResponse):
    type: Literal["sessionInit"]
    payload: Optional[InitSessionResponsePayload]


class EventResponsePayload(BaseModel):
    result: Any
    mutations: Dict[str, Any]
    mail: List
    components: Optional[Dict] = None


class StateEnquiryResponsePayload(BaseModel):
    mutations: Dict[str, Any]
    mail: List


class StateContentResponsePayload(BaseModel):
    state: Dict[str, Any]


class EventResponse(AppProcessServerResponse):
    type: Literal["event"]
    payload: Optional[EventResponsePayload] = None


class StateEnquiryResponse(AppProcessServerResponse):
    type: Literal["stateEnquiry"]
    payload: Optional[StateEnquiryResponsePayload]


class HashRequestResponsePayload(BaseModel):
    message: str


class HashRequestResponse(AppProcessServerRequest):
    type: Literal["hashRequest"]
    payload: HashRequestResponsePayload


AppProcessServerResponsePacket = Tuple[int, Optional[str], AppProcessServerResponse]


class DataFrameRecordAdded(TypedDict):
    record: Dict[str, Any]


class DataFrameRecordUpdated(TypedDict):
    record_index: int
    record: Dict[str, Any]


class DataFrameRecordRemoved(TypedDict):
    record_index: int


class WriterEventResult(TypedDict):
    ok: bool
    result: Any


class MetadataDefinition(TypedDict):
    """
    Declarative definition of meta for auto-completion
    """

    writer_version: str


class ComponentDefinition(TypedDict):
    """
    Declarative definition of a component for auto-completion
    """

    id: str
    type: str
    content: Dict[str, Any]
    isCodeManaged: Optional[bool]
    position: int
    parentId: Optional[str]
    handlers: Optional[Dict[str, str]]
    visible: Optional[Union[bool, str]]
    binding: Optional[Dict]
    outs: Optional[Dict[str, str]]
    x: Optional[int]
    y: Optional[int]
    featureFlags: Optional[List[str]]


class BlueprintExecutionLog(BaseModel):
    runId: str
    summary: List[Dict]
    exit: Optional[str] = None


class BlueprintExecutionError(Exception):
    """Exception raised when a blueprint execution fails."""
    def __init__(
            self,
            message: Optional[str] = "An error occurred "
                                     "during blueprint execution."
    ):
        super().__init__(message)
        self.message = message


class WriterConfigurationError(ValueError):
    pass
