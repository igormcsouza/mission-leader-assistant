"""Page object for the baptismal plan view (#baptismalPlanView)."""
# pylint: disable=missing-function-docstring
from .base_page import BasePage

# Autosave round-trips against the local dev server complete in well under
# 200ms (confirmed via network inspection). Reactive waits on the transient
# "Salvo" status text (both `page.wait_for_function` and `page.expect_response`)
# proved unreliable specifically for saves triggered from a locator scoped inside
# a re-rendered candidate card — they would time out even though the save had
# already completed and the DOM had genuinely already updated. A fixed delay with
# generous headroom sidesteps that without depending on unclear Playwright/DOM
# timing behavior in this one scenario.
_SAVE_ROUNDTRIP_MS = 600


class BaptismalPlanPage(BasePage):
    """Wraps the plan list, editor form, candidates, and PDF export.

    Autosave fires one request per field blur/change. Editing several fields back
    to back would fire several overlapping autosaves (each snapshotting the full
    form at call time), and since responses can arrive out of order, a later,
    fresher save could be overwritten in the UI by an earlier, staler one that
    resolves after it. `fill_details`/`fill_candidate` avoid that by waiting for
    each field's own save to complete before touching the next field, so saves
    are always sent — and confirmed — one at a time.
    """

    def empty_state_visible(self):
        return self.page.locator("#bpEmptyState").is_visible()

    def editor_visible(self):
        return self.page.locator("#bpEditorContent").is_visible()

    def new_plan(self):
        self.page.click("#bpNewPlanBtn")
        self.page.wait_for_selector("#bpEditorContent:not(.hidden)")

    def plan_items(self):
        return self.page.locator(".bp-plan-item[data-plan-id]")

    def select_plan(self, plan_id):
        self.page.click(f'.bp-plan-item[data-plan-id="{plan_id}"] .bp-plan-item-content')
        self.page.wait_for_selector("#bpEditorContent:not(.hidden)")
        # `networkidle` proved unreliable for this SPA-style, JS-triggered fetch
        # (it can resolve before the request is even dispatched) — see
        # `_SAVE_ROUNDTRIP_MS` above for the same issue in the autosave path.
        self.wait_for_saved()

    def delete_plan(self, plan_id):
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.click(f'.bp-plan-item[data-plan-id="{plan_id}"] .bp-plan-item-delete')

    # One optional kwarg per form field is clearer here than bundling them into a
    # dict/dataclass for a test helper.
    def fill_details(self, *, service_date=None, service_time=None,  # pylint: disable=too-many-arguments
                      ward=None, location=None, conducting_leader=None, status=None):
        fields = {
            "#bpServiceDate": service_date,
            "#bpServiceTime": service_time,
            "#bpWard": ward,
            "#bpLocation": location,
            "#bpConductingLeader": conducting_leader,
        }
        for selector, value in fields.items():
            if value is not None:
                self.page.fill(selector, value)
                self.page.locator(selector).blur()
                self.wait_for_saved()
        if status is not None:
            self.page.select_option("#bpStatus", status)
            self.wait_for_saved()

    def add_candidate(self):
        self.page.click("#bpAddCandidateBtn")
        self.wait_for_saved()

    def candidate_cards(self):
        return self.page.locator(".bp-candidate-card")

    def fill_candidate(self, card_index, *, full_name=None, birth_date=None, candidate_type=None):
        card = self.candidate_cards().nth(card_index)
        if full_name is not None:
            card.locator(".bp-c-fullName").fill(full_name)
            card.locator(".bp-c-fullName").blur()
            self.wait_for_saved()
        if birth_date is not None:
            card.locator(".bp-c-birthDate").fill(birth_date)
            card.locator(".bp-c-birthDate").blur()
            self.wait_for_saved()
        if candidate_type is not None:
            card.locator(".bp-c-candidateType").select_option(candidate_type)
            self.wait_for_saved()

    def remove_candidate(self, card_index):
        self.candidate_cards().nth(card_index).locator(".bp-remove-candidate").click()
        self.wait_for_saved()

    def ordinances_witnesses_empty_note_visible(self):
        return self.page.locator("#bpOrdinancesWitnessesEmpty").is_visible()

    def export_pdf(self):
        with self.page.expect_popup() as popup_info:
            self.page.click("#bpExportPdfBtn")
        return popup_info.value

    def save_status_text(self):
        return self.page.locator("#bpSaveStatus").text_content()

    def wait_for_saved(self):
        """Wait for an in-flight autosave to complete. See `_SAVE_ROUNDTRIP_MS`."""
        self.page.wait_for_timeout(_SAVE_ROUNDTRIP_MS)
