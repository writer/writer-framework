from writer.blocks.addtostatelist import AddToStateList
from writer.blocks.calleventhandler import CallEventHandler
from writer.blocks.changepage import ChangePage
from writer.blocks.code import CodeBlock
from writer.blocks.foreach import ForEach
from writer.blocks.httprequest import HTTPRequest
from writer.blocks.logmessage import LogMessage
from writer.blocks.parsejson import ParseJSON
from writer.blocks.returnvalue import ReturnValue
from writer.blocks.runblueprint import RunBlueprint
from writer.blocks.setstate import SetState
from writer.blocks.uieventtrigger import UIEventTrigger
from writer.blocks.writeraddchatmessage import WriterAddChatMessage
from writer.blocks.writeraddtokg import WriterAddToKG
from writer.blocks.writeraskkg import WriterAskGraphQuestion
from writer.blocks.writerchat import WriterChat
from writer.blocks.writerclassification import WriterClassification
from writer.blocks.writercompletion import WriterCompletion
from writer.blocks.writerfileapi import WriterUploadFile
from writer.blocks.writerinitchat import WriterInitChat
from writer.blocks.writernocodeapp import WriterNoCodeApp
from writer.blocks.writerparsepdf import WriterParsePDFByFileID
from writer.blocks.writertoolcalling import WriterToolCalling

SetState.register("blueprints_setstate")
WriterClassification.register("blueprints_writerclassification")
WriterCompletion.register("blueprints_writercompletion")
HTTPRequest.register("blueprints_httprequest")
RunBlueprint.register("blueprints_runblueprint")
WriterNoCodeApp.register("blueprints_writernocodeapp")
ForEach.register("blueprints_foreach")
LogMessage.register("blueprints_logmessage")
WriterChat.register("blueprints_writerchat")
WriterAddChatMessage.register("blueprints_writeraddchatmessage")
ParseJSON.register("blueprints_parsejson")
CallEventHandler.register("blueprints_calleventhandler")
AddToStateList.register("blueprints_addtostatelist")
ReturnValue.register("blueprints_returnvalue")
WriterInitChat.register("blueprints_writerinitchat")
WriterAddToKG.register("blueprints_writeraddtokg")
UIEventTrigger.register("blueprints_uieventtrigger")
CodeBlock.register("blueprints_code")
ChangePage.register("blueprints_changepage")
WriterToolCalling.register("blueprints_writertoolcalling")
WriterAskGraphQuestion.register("blueprints_writeraskgraphquestion")
WriterParsePDFByFileID.register("blueprints_writerparsepdf")
WriterUploadFile.register("blueprints_writeruploadfile")