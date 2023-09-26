from typing import Any, Dict, List, Optional, Protocol, Tuple
from pydantic import BaseModel
from typing_extensions import TypedDict, Literal

class StreamsyncFileItem(TypedDict):
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
                      "event", "codeUpdate", "codeSave", "checkSession", "keepAlive", "stateEnquiry"]

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


class InitResponseBodyRun(InitResponseBody):
    mode: Literal["run"]


class InitResponseBodyEdit(InitResponseBody):
    mode: Literal["edit"]
    runCode: Optional[str] = None


class StreamsyncWebsocketIncoming(BaseModel):
    type: str
    trackingId: int
    payload: Dict[str, Any]


class StreamsyncWebsocketOutgoing(BaseModel):
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


class StreamsyncEvent(BaseModel):
    type: str
    instancePath: InstancePath
    payload: Optional[Any] = None


class EventRequest(AppProcessServerRequest):
    type: Literal["event"]
    payload: StreamsyncEvent


class StateEnquiryRequest(AppProcessServerRequest):
    type: Literal["stateEnquiry"]


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


class InitSessionResponse(AppProcessServerResponse):
    type: Literal["sessionInit"]
    payload: Optional[InitSessionResponsePayload]


class EventResponsePayload(BaseModel):
    result: Any
    mutations: Dict[str, Any]
    mail: List


class StateEnquiryResponsePayload(BaseModel):
    mutations: Dict[str, Any]
    mail: List


class EventResponse(AppProcessServerResponse):
    type: Literal["event"]
    payload: Optional[EventResponsePayload] = None


class StateEnquiryResponse(AppProcessServerResponse):
    type: Literal["stateEnquiry"]
    payload: Optional[StateEnquiryResponsePayload]


AppProcessServerResponsePacket = Tuple[int,
                                       Optional[str], AppProcessServerResponse]


class StreamsyncEventResult(TypedDict):
    ok: bool
    result: Any
