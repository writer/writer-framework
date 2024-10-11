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
    def read(self) -> Any:
        ...


ServeMode = Literal["run", "edit"]
MessageType = Literal["sessionInit", "componentUpdate",
                      "event", "codeUpdate", "codeSave", "checkSession",
                      "keepAlive", "stateEnquiry", "setUserinfo", "stateContent"]


class AbstractTemplate(BaseModel):
    baseType: str
    writer: Dict

# Web server models


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


class InitResponseBodyRun(InitResponseBody):
    mode: Literal["run"]


class InitResponseBodyEdit(InitResponseBody):
    mode: Literal["edit"]
    runCode: Optional[str] = None


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


class WriterEvent(BaseModel):
    type: str
    instancePath: InstancePath
    payload: Optional[Any] = None


class EventRequest(AppProcessServerRequest):
    type: Literal["event"]
    payload: WriterEvent


class StateEnquiryRequest(AppProcessServerRequest):
    type: Literal["stateEnquiry"]


class StateContentRequest(AppProcessServerRequest):
    type: Literal["stateContent"]


AppProcessServerRequestPacket = Tuple[int,
                                      Optional[str], AppProcessServerRequest]

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


AppProcessServerResponsePacket = Tuple[int, Optional[str], AppProcessServerResponse]


class DataframeRecordAdded(TypedDict):
    record: Dict[str, Any]

class DataframeRecordUpdated(TypedDict):
    record_index: int
    record: Dict[str, Any]

class DataframeRecordRemoved(TypedDict):
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

