from typing import Any, Dict, List, Literal, Optional, Protocol, Tuple, TypedDict
from pydantic import BaseModel


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
                      "event", "codeUpdate", "codeSave", "checkSession", "keepAlive"]

# Web server models


class InitRequestBody(BaseModel):
    proposedSessionId: Optional[str]


class InitResponseBody(BaseModel):
    mode: Literal["run", "edit"]
    sessionId: str
    userState: Dict[str, Any]
    mail: List[Any]
    components: Dict[str, Any]


class InitResponseBodyRun(InitResponseBody):
    mode: Literal["run"]


class InitResponseBodyEdit(InitResponseBody):
    mode: Literal["edit"]
    userFunctions: List[str]
    savedCode: Optional[str]
    runCode: Optional[str]


class StreamsyncWebsocketIncoming(BaseModel):
    type: str
    trackingId: int
    payload: Dict[str, Any]


class StreamsyncWebsocketOutgoing(BaseModel):
    messageType: str
    trackingId: int
    payload: Optional[Dict[str, Any]]

# AppProcessServer Requests


class AppProcessServerRequest(BaseModel):
    type: MessageType
    payload: Optional[Any]


class InitSessionRequestPayload(BaseModel):
    cookies: Optional[Dict[str, str]]
    headers: Optional[Dict[str, str]]
    proposedSessionId: Optional[str]


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
    payload: Optional[Any]


class EventRequest(AppProcessServerRequest):
    type: Literal["event"]
    payload: StreamsyncEvent


AppProcessServerRequestPacket = Tuple[int,
                                      Optional[str], AppProcessServerRequest]

# AppProcessServer Responses


class AppProcessServerResponse(BaseModel):
    status: Literal["ok", "error"]
    status_message: Optional[str]
    payload: Optional[Any]


class InitSessionResponsePayload(BaseModel):
    sessionId: str
    userState: Dict[str, Any]
    mail: List
    userFunctions: List[str]
    components: Dict


class InitSessionResponse(AppProcessServerResponse):
    type: Literal["sessionInit"]
    payload: Optional[InitSessionResponsePayload]


class EventResponsePayload(BaseModel):
    result: Any
    mutations: Dict[str, Any]
    mail: List


class EventResponse(AppProcessServerResponse):
    type: Literal["event"]
    payload: Optional[EventResponsePayload]


AppProcessServerResponsePacket = Tuple[int,
                                       Optional[str], AppProcessServerResponse]


class StreamsyncEventResult(TypedDict):
    ok: bool
    result: Any
