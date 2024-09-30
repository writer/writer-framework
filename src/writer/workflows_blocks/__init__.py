from writer.workflows_blocks.httprequest import HTTPRequest
from writer.workflows_blocks.setstate import SetState
from writer.workflows_blocks.writerclassification import WriterClassification
from writer.workflows_blocks.writercompletion import WriterCompletion
from writer.workflows_blocks.runworkflow import RunWorkflow

SetState.register("workflows_setstate")
WriterClassification.register("workflows_writerclassification")
WriterCompletion.register("workflows_writercompletion")
HTTPRequest.register("workflows_httprequest")
RunWorkflow.register("workflows_runworkflow")