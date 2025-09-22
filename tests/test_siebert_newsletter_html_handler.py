import pytest

from core.infrastructure.workflows.handlers.siebert_newsletter_html_handler import (
    SiebertNewsletterHtmlHandler,
)


@pytest.fixture
def handler():
    return SiebertNewsletterHtmlHandler("siebert_newsletter_html")


def test_validate_html_output_passes_for_valid_container(handler):
    html = (
        '<div style="max-width: 600px; margin: 0 auto; font-family: Arial;">'
        '<p style="margin:0">Hello world</p>'
        "</div><!-- QUALITY CHECKLIST: ok -->"
    )
    errors = handler._validate_html_output(html)
    assert errors == []


def test_validate_html_output_detects_banned_tags(handler):
    html = '<div style="max-width: 600px"><body>bad</body></div>'
    errors = handler._validate_html_output(html)
    assert any("banned structural tags" in err for err in errors)


def test_validate_html_output_requires_max_width(handler):
    html = '<div style="padding:16px">Missing width</div>'
    errors = handler._validate_html_output(html)
    assert any("max-width" in err for err in errors)


def test_validate_html_output_requires_quality_checklist(handler):
    html = (
        '<div style="max-width: 600px; margin: 0 auto; font-family: Arial;">'
        "<p>Missing checklist</p>"
        "</div>"
    )
    errors = handler._validate_html_output(html)
    assert any("QUALITY CHECKLIST" in err for err in errors)


def test_validate_html_output_blocks_class_attribute(handler):
    html = '<div style="max-width: 600px" class="wrapper">Bad attr</div>'
    errors = handler._validate_html_output(html)
    assert any("forbidden attributes" in err for err in errors)


def test_prepare_context_injects_design_system(handler):
    context = handler.prepare_context({"topic": "Markets", "target_word_count": 900})
    assert "html_design_system_instructions" in context
    assert context["workflow_output_format"] == "html"


def test_post_process_task_raises_on_invalid_html(handler):
    context = {}
    with pytest.raises(ValueError):
        handler.post_process_task("task5_html_builder", "<div>bad</div>", context)
