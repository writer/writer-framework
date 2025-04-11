from unittest.mock import MagicMock, patch

import pytest
from writer.blocks.writerparsepdf import WriterParsePDF, WriterParsePDFByFileID


@pytest.mark.asyncio
async def test_parse_pdf_success_markdown_enabled(session, runner):
    file_dict = {
        "type": "application/pdf",
        "data": "base64-data",
        "name": "report.pdf"
    }

    with patch("writer.ai.upload_file") as mock_upload, \
         patch("writer.ai.WriterAIManager.acquire_client") as mock_client:

        mock_uploaded_file = MagicMock()
        mock_uploaded_file.id = "file-123"
        mock_upload.return_value = mock_uploaded_file

        mock_response = MagicMock()
        mock_response.content = "# PDF Report"
        mock_client.return_value.tools.parse_pdf.return_value = mock_response

        component = session.add_fake_component(
            {}
        )
        block = WriterParsePDF(component, runner, {})
        block._get_field = lambda name, *args, **kwargs: file_dict if name == "file" else "yes"

        block.run()

        mock_upload.assert_called_once_with(**file_dict)
        mock_client.return_value.tools.parse_pdf.assert_called_once_with("file-123", format="markdown")
        assert block.result == "# PDF Report"
        assert block.outcome == "success"


@pytest.mark.asyncio
async def test_parse_pdf_non_pdf_type(session, runner):
    file_dict = {
        "type": "text/plain",
        "data": "some-text",
        "name": "note.txt"
    }

    component = session.add_fake_component(
        {}
    )
    block = WriterParsePDF(component, runner, {})
    block._get_field = lambda name, *args, **kwargs: file_dict if name == "file" else "yes"

    with pytest.raises(ValueError, match="File input must be a PDF file."):
        block.run()


@pytest.mark.asyncio
async def test_parse_pdf_missing_required_keys(session, runner):
    file_dict = {
        "type": "application/pdf",
        # 'data' is missing
        "name": "badfile.pdf"
    }

    component = session.add_fake_component(
        {}
    )
    block = WriterParsePDF(component, runner, {})
    block._get_field = lambda name, *args, **kwargs: file_dict if name == "file" else "no"

    with pytest.raises(ValueError, match="File input must contain 'data'"):
        block.run()


@pytest.mark.asyncio
async def test_parse_pdf_input_is_list_of_multiple_files(session, runner):
    file_dicts = [
        {"type": "application/pdf", "data": "data1"},
        {"type": "application/pdf", "data": "data2"}
    ]

    component = session.add_fake_component(
        {}
    )
    block = WriterParsePDF(component, runner, {})
    block._get_field = lambda name, *args, **kwargs: file_dicts if name == "file" else "yes"

    with pytest.raises(ValueError, match="File input must be a single file object."):
        block.run()


@pytest.mark.asyncio
async def test_parse_pdf_input_not_a_dict(session, runner):
    file_input = "not_a_dict"

    component = session.add_fake_component(
        {}
    )
    block = WriterParsePDF(component, runner, {})
    block._get_field = lambda name, *args, **kwargs: file_input if name == "file" else "yes"

    with pytest.raises(ValueError, match="File input must be a dictionary"):
        block.run()


@pytest.mark.asyncio
async def test_parse_pdf_error_fallback(session, runner):
    file_dict = {
        "type": "application/pdf",
        "data": "broken-data",
        "name": "file.pdf"
    }

    with patch("writer.ai.upload_file", side_effect=Exception("Upload failed")):
        component = session.add_fake_component(
            {}
        )
        block = WriterParsePDF(component, runner, {})
        block._get_field = lambda name, *args, **kwargs: file_dict if name == "file" else "yes"

        with pytest.raises(Exception, match="Upload failed"):
            block.run()
        assert block.outcome == "error"


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