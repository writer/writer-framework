from writer.blocks.addtostatelist import AddToStateList
from writer.blocks.calleventhandler import CallEventHandler
from writer.blocks.foreach import ForEach
from writer.blocks.httprequest import HTTPRequest
from writer.blocks.logmessage import LogMessage
from writer.blocks.parsejson import ParseJSON
from writer.blocks.returnvalue import ReturnValue
from writer.blocks.runworkflow import RunWorkflow
from writer.blocks.setstate import SetState
from writer.blocks.writeraddchatmessage import WriterAddChatMessage
from writer.blocks.writeraddtokg import WriterAddToKG
from writer.blocks.writerchat import WriterChat
from writer.blocks.writerclassification import WriterClassification
from writer.blocks.writercompletion import WriterCompletion
from writer.blocks.writerinitchat import WriterInitChat
from writer.blocks.writernocodeapp import WriterNoCodeApp

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
CallEventHandler.register("workflows_calleventhandler")
AddToStateList.register("workflows_addtostatelist")
ReturnValue.register("workflows_returnvalue")
WriterInitChat.register("workflows_writerinitchat")
WriterAddToKG.register("workflows_writeraddtokg")
