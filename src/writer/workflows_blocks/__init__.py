from writer.workflows_blocks.foreach import ForEach
from writer.workflows_blocks.httprequest import HTTPRequest
from writer.workflows_blocks.logmessage import LogMessage
from writer.workflows_blocks.parsejson import ParseJSON
from writer.workflows_blocks.runworkflow import RunWorkflow
from writer.workflows_blocks.setstate import SetState
from writer.workflows_blocks.writeraddchatmessage import WriterAddChatMessage
from writer.workflows_blocks.writerchat import WriterChat
from writer.workflows_blocks.writerclassification import WriterClassification
from writer.workflows_blocks.writercompletion import WriterCompletion
from writer.workflows_blocks.writernocodeapp import WriterNoCodeApp

SetState.register("workflows_setstate")
WriterClassification.register("workflows_writerclassification")
WriterCompletion.register("workflows_writercompletion")
HTTPRequest.register("workflows_httprequest")
RunWorkflow.register("workflows_runworkflow")
WriterNoCodeApp.register("workflows_writernocodeapp")
ForEach.register("workflows_foreach")
LogMessage.register("workflows_logmessage")
WriterChat.register("workflows_writerchat")
WriterAddChatMessage.register("workflows_writeraddchatmessage")
ParseJSON.register("workflows_parsejson")