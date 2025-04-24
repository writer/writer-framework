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
from writer.blocks.writer_kg_crud_list import (
    WriterCreateGraph,
    WriterDeleteGraph,
    WriterListGraphs,
    WriterRetrieveGraph,
    WriterUpdateGraph,
)
from writer.blocks.writeraddchatmessage import WriterAddChatMessage
from writer.blocks.writeraddtokg import WriterAddToKG
from writer.blocks.writeraskkg import WriterAskGraphQuestion
from writer.blocks.writerchat import WriterChat
from writer.blocks.writerclassification import WriterClassification
from writer.blocks.writercompletion import WriterCompletion
from writer.blocks.writerfileapi import (
    WriterDeleteFile,
    WriterDownloadFile,
    WriterListFiles,
    WriterRetrieveFile,
    WriterRetryFiles,
    WriterUploadFile,
)
from writer.blocks.writerinitchat import WriterInitChat
from writer.blocks.writernocodeapp import WriterNoCodeApp
from writer.blocks.writerremovefromkg import WriterRemoveFromKG
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
WriterRemoveFromKG.register("blueprints_writerremovefromkg")
UIEventTrigger.register("blueprints_uieventtrigger")
CodeBlock.register("blueprints_code")
ChangePage.register("blueprints_changepage")
WriterToolCalling.register("blueprints_writertoolcalling")
WriterCreateGraph.register("blueprints_writercreategraph")
WriterRetrieveGraph.register("blueprints_writerretrievegraph")
WriterUpdateGraph.register("blueprints_writerupdategraph")
WriterDeleteGraph.register("blueprints_writerdeletegraph")
WriterListGraphs.register("blueprints_writerlistgraphs")
WriterAskGraphQuestion.register("blueprints_writeraskgraphquestion")
WriterUploadFile.register("blueprints_writeruploadfile")
WriterListFiles.register("blueprints_writerlistfiles")
WriterDeleteFile.register("blueprints_writerdeletefile")
WriterDownloadFile.register("blueprints_writerdownloadfile")
WriterRetryFiles.register("blueprints_writerretryfiles")
WriterRetrieveFile.register("blueprints_writerretrievefile")
