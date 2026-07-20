"""Covers Baptismal Plan PDF export (`#bpExportPdfBtn`, commit 6107848).

The export opens a same-origin popup, writes a printable HTML document into it, and
calls `window.print()` on load. Headless Chromium's print dialog cannot be driven by
Playwright, so this only asserts on the popup's rendered document content.
"""
# pylint: disable=missing-function-docstring


def test_export_opens_popup_with_plan_content(baptismal_plan_page):
    baptismal_plan_page.new_plan()
    baptismal_plan_page.add_candidate()
    baptismal_plan_page.fill_candidate(0, full_name="Maria Oliveira")

    popup = baptismal_plan_page.export_pdf()
    popup.wait_for_load_state()

    assert popup.locator("h1").text_content() == "Planejamento Batismal"
    assert "Maria Oliveira" in popup.content()
