# E2E Coverage Tracker

Keep this file in sync with `e2e/tests/`. When you add or modify a test, update the
matching row (or add a new one).

Statuses: `Covered` | `Partial` | `Planned` | `N/A (unmerged)` | `N/A (no interactive surface)`

**Before adding a row against a commit**, verify it is actually reachable from `main`:

```
git merge-base --is-ancestor <commit> HEAD && echo "on main" || echo "NOT on main"
```

Two rows below (#4 and #15) were only caught by this check — their commits exist in
history but live on branches that were never merged, so no code for them exists on
`main` and no test was written.

| # | Feature / Bugfix | Commit(s) | Test file | Test name(s) | Status | Notes |
|---|---|---|---|---|---|---|
| 1 | Auth / dev-mode bypass | 45e3799, e4ec5c7 | `test_devmode_bootstrap.py` | `test_api_config_reports_dev_mode`, `test_login_view_is_skipped`, `test_drawer_shows_local_user`, `test_api_calls_carry_local_user_header` | Covered | |
| 2 | Lunch/visit calendar core | f467a0d, 552e70d, e5a70ac | `test_calendar_core.py` | `test_default_month_is_current_month`, `test_monday_is_locked_to_pday`, `test_two_name_slots_persist_independently_after_reload`, `test_empty_padding_cells_render_without_inputs` | Covered | |
| 3 | PDAY override / mute day | (core UI, undated) | `test_calendar_pday_and_mute.py` | `test_pday_override_moves_names_into_monday_preview`, `test_pday_override_can_be_reverted_by_reselecting_monday`, `test_mute_toggle_disables_inputs_for_that_day`, `test_mute_toggle_can_be_reverted` | Covered | |
| 4 | Duplas Missionárias 3-couple slider | e5a70ac, c3c3459, 30e8730, 627da17, 69ea4b9 | — | — | N/A (unmerged) | Lives on `origin/copilot/add-third-missionary-option`, never merged to `main`. Current `renderCalendar()` hard-codes exactly 2 slots. Re-add coverage if/when merged. |
| 5 | PNG export | (part of core calendar) | `test_calendar_download_png.py` | `test_download_produces_dated_png_and_status_message` | Covered | |
| 6 | Multi-profile (Perfil) | 999ded9 | `test_multi_profile.py` | `test_exactly_two_profile_buttons`, `test_switching_profile_keeps_entries_independent`, `test_profile_outside_configured_range_is_rejected_by_the_api` | Covered | |
| 7 | Ward setting / per-profile title-subtitle | 496892f | `test_settings_ward_and_titles.py` | `test_settings_modal_prefills_current_ward`, `test_save_persists_ward_and_profile_title_after_reload`, `test_cancel_discards_unsaved_edits` | Covered | |
| 8 | Baptismal Plan CRUD | 6107848 | `test_baptismal_plan_crud.py` | `test_empty_state_shown_with_no_plans`, `test_new_plan_appears_in_list_with_default_status`, `test_editing_details_autosaves`, `test_add_candidate_autosaves_and_populates_ordinances_section`, `test_remove_candidate_autosaves`, `test_delete_plan_removes_it_and_shows_empty_state`, `test_switching_between_existing_plans_loads_correct_data`, `test_reload_persists_plan_data` | Covered | |
| 9 | Baptismal Plan PDF export | 6107848 | `test_baptismal_plan_export_pdf.py` | `test_export_opens_popup_with_plan_content` | Covered | Only asserts popup content, not the native OS print dialog (not automatable in headless Chromium). |
| 10 | Side navigation drawer | 85ebcd9 | `test_side_drawer_navigation.py` | `test_drawer_starts_closed`, `test_menu_button_opens_and_backdrop_closes_drawer`, `test_nav_items_are_calendar_and_baptismal_plan`, `test_navigating_switches_view_and_closes_drawer`, `test_dev_mode_sign_out_closes_drawer_without_error` | Covered | |
| 11 | Mobile/responsive UI | ce4aeca, d42be9c | `test_responsive_mobile.py` | `test_menu_button_visible_and_drawer_overlays`, `test_calendar_table_scrolls_horizontally_on_mobile` | Partial | Structural/behavioral checks only, no pixel snapshots. |
| 12 | Loading states | 8bd0b8d | `test_loading_states.py` | `test_calendar_spinner_shows_while_initial_data_loads`, `test_baptismal_plan_save_status_transitions_while_saving` | Covered | Uses `page.route` to inject artificial delay. |
| 13 | Data persistence: clearing a field | b593f26 | `test_persistence_regressions.py` | `test_clearing_a_cell_persists_as_empty` | Covered | Explicit regression test. |
| 14 | Calendar cell overflow | 1bd7879 | `test_persistence_regressions.py` | `test_long_names_do_not_overflow_the_cell` | Partial | Fuzzy bounding-box comparison, not a strict CSS regression test. |
| 15 | Deprecation notice | bf08145 | — | — | N/A (unmerged) | Lives on `origin/deprecated-v0.4`, never merged to `main`. No such element exists. |
| 16 | Dark mode | 552e70d | `test_ui_smoke.py` | `test_color_scheme_is_dark` | Covered | Static `color-scheme: dark` CSS rule — no interactive toggle exists in the current UI. |
| 17 | Favicon/branding & page title | 857dded | `test_ui_smoke.py` | `test_page_title`, `test_favicon_link_and_asset` | Covered | |
