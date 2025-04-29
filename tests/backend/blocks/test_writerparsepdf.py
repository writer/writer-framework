from unittest.mock import MagicMock, patch

import pytest
from writer.blocks.writerparsepdf import WriterParsePDFByFileID


@pytest.mark.asyncio
async def test_parse_pdf_by_file_id_success_markdown(session, runner):
    file_id = "file-uuid-456"

    with patch("writer.ai.WriterAIManager.acquire_client") as mock_client:
        mock_response = MagicMock()
        mock_response.content = "## Parsed Markdown Output"
        mock_client.return_value.tools.parse_pdf.return_value = mock_response

        component = session.add_fake_component({})
        block = WriterParsePDFByFileID(component, runner, {})
        block._get_field = lambda name, *args, **kwargs: file_id if name == "file" else "yes"

        block.run()

        mock_client.return_value.tools.parse_pdf.assert_called_once_with(file_id, format="markdown")
        assert block.result == "## Parsed Markdown Output"
        assert block.outcome == "success"


@pytest.mark.asyncio
async def test_parse_pdf_by_file_id_success_plain_text(session, runner):
    file_id = "file-uuid-789"

    with patch("writer.ai.WriterAIManager.acquire_client") as mock_client:
        mock_response = MagicMock()
        mock_response.content = "Plain text output"
        mock_client.return_value.tools.parse_pdf.return_value = mock_response

        component = session.add_fake_component({})
        block = WriterParsePDFByFileID(component, runner, {})
        block._get_field = lambda name, *args, **kwargs: file_id if name == "file" else "no"

        block.run()

        mock_client.return_value.tools.parse_pdf.assert_called_once_with(file_id, format="text")
        assert block.result == "Plain text output"
        assert block.outcome == "success"


@pytest.mark.asyncio
async def test_parse_pdf_by_file_id_error(session, runner):
    file_id = "file-uuid-bad"

    with patch("writer.ai.WriterAIManager.acquire_client") as mock_client:
        mock_client.return_value.tools.parse_pdf.side_effect = Exception("Parse failed")

        component = session.add_fake_component({})
        block = WriterParsePDFByFileID(component, runner, {})
        block._get_field = lambda name, *args, **kwargs: file_id if name == "file" else "yes"

        with pytest.raises(Exception, match="Parse failed"):
            block.run()
        assert block.outcome == "error"
