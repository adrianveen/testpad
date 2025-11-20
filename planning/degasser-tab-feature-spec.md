# New Feature: Dissolved Oxygen Data Tab

## 1. Purpose
The purpose of this feature is to allow users to enter recorded data:
- Pass/Fail test results
- Data Measurements
- DO Levels at specific time intervals

And then produce a formatted, 1 page report with the data plotted as well. The report will be available for download as a PDF. The purpose of the report is to be packaged with the dissolved oxygen meters that are purchased.
## 2. User Flow
1. User navigates to the "Dissolved Oxygen Data" tab in the application.
2. User is presented with a form to input information and data
3. User fills out the form and submits the data.
4. The application processes the data and generates a formatted report.
## 3. Inputs

| Source | Presenter hand-off | Model / State target | Notes |
| --- | --- | --- | --- |
| **User → Name / Date / Location fields** | `presenter.capture_metadata(name, date, location)` | Future metadata state object (to be persisted alongside model state) | Manual entry coming straight from the operator. |
| **User → DS-50 Serial Number** | `presenter.capture_serial(number)` | Same metadata state object | Stored with report header details. |
| **User → Vacuum Pressure pass/fail** | `presenter.update_test_row("vacuum_pressure", pass_fail=value)` | `model.update_test_row(index=0, pass_fail=value)` | Index mapping follows `DEFAULT_TEST_DESCRIPTIONS`. |
| **User → Vacuum Pressure measured value** | `presenter.update_test_row("vacuum_pressure", measured=value)` | `model.update_test_row(index=0, measured=value)` | Presenter validates numeric input before passing to model. |
| **User → Vacuum Pressure spec min/max overrides** | `presenter.update_test_row("vacuum_pressure", spec_min=value, spec_max=value)` | `model.update_test_row(index=0, spec_min=value/spec_max=value)` | Compare against DS-50 defaults; raise presenter-level error if mismatched (planned). |
| **User → Flow Rate pass/fail** | `presenter.update_test_row("flow_rate", pass_fail=value)` | `model.update_test_row(index=1, pass_fail=value)` | Same pathway for other editable columns (spec min/max). |
| **User → Flow Rate measured value** | `presenter.update_test_row("flow_rate", measured=value)` | `model.update_test_row(index=1, measured=value)` | Value expected in mL/min. |
| **User → Flow Rate spec min/max overrides** | `presenter.update_test_row("flow_rate", spec_min=value, spec_max=value)` | `model.update_test_row(index=1, spec_min=value/spec_max=value)` | Validate against default thresholds per DS-50 model; mismatch surfaces an error. |
| **User → Dissolved O₂ level test pass/fail** | `presenter.update_test_row("do_level", pass_fail=value)` | `model.update_test_row(index=2, pass_fail=value)` | |
| **User → Dissolved O₂ level measured value** | `presenter.update_test_row("do_level", measured=value)` | `model.update_test_row(index=2, measured=value)` | mg/L entry. |
| **User → Dissolved O₂ level spec min overrides** | `presenter.update_test_row("do_level", spec_max=value)` | `model.update_test_row(index=2, spec_max=value)` | Max expected <3 mg/L; presenter checks against DS-50 defaults. |
| **User → Re-circulation test measured/pass-fail details** | `presenter.update_test_row("recirculation", pass_fail=value, measured=value)` | `model.update_test_row(index=3, pass_fail=value/measured=value)` | Presenter splits the sub-fields (time to 4 mg/L, etc.) into the table row or future sub-structure. |
| **User → Re-circulation spec/time limits** | `presenter.update_test_row("recirculation", spec_min=value, spec_max=value)` | `model.update_test_row(index=3, spec_min=value/spec_max=value)` | Defaults: 7 mg/L start, 5 min to 4 mg/L, 10 min to 2 mg/L; presenter raises when outside spec (planned). |
| **User → Manual time-series minute edit** | `presenter.handle_time_series_edit(minute)` | `model.set_measurement(minute, value)` | Minute defaults come from model; presenter reacts if user overrides. |
| **User → Manual time-series O₂ value edit** | `presenter.handle_time_series_edit(minute, oxygen)` | `model.set_measurement(minute, oxygen)` | Model enforces 0..10 minutes and >0 mg/L via `_validate_*`. |
| **User → Temperature entry** | `presenter.handle_temperature(value)` | `model.set_temperature(value)` | Optional field; presenter clears via `model.clear_temperature()` when blanked. |
| **Disk → CSV import** | `presenter.load_from_csv(path)` | `model.load_from_csv(path)` | Disk-sourced data overwrites the current time-series and temperature. |
| **User → Clear measurement action** | `presenter.clear_measurement(minute)` | `model.clear_measurement(minute)` | Triggered by UI “clear” control per minute slot. |
| **User → Reset tab** | `presenter.reset()` | `model.reset()` + metadata reset | Restores defaults and clears transient state. |
## 4. Outputs

### Reporting & export pipeline

| Source | Presenter hand-off | Model / State target | Notes |
| --- | --- | --- | --- |
| **User → Generate Report action** | `presenter.generate_report()` | Calls `model.generate_report()` in background thread; returns `ReportResult` | Presenter manages UI state (disable inputs, show progress) during generation. |
| **Model → Report generation result** | `model.generate_report()` returns `ReportResult` | `ReportResult` dataclass with `pdf_bytes` or `error` | Presenter handles success (show save dialog) or failure (show error message). |
| **User → Save Report action** | `presenter.save_report(path)` | Writes `ReportResult.pdf_bytes` to disk at `path` | Presenter shows file dialog; handles IO errors and user cancellation. |
| **User → Report generation error** | `presenter.handle_report_error(error)` | N/A | Presenter shows error message in UI; logs full details. |
| **User → Export CSV action** | `presenter.export_to_csv(path)` | `model.export_csv(path)` | Writes current time-series and temperature to user-specified path. |
| **Model → CSV export result** | `model.export_csv(path)` success/exception | Presenter wraps success messaging; surfaces errors to the user. |
| **User → CSV export error** | `presenter.handle_export_error(error)` | N/A | Presenter shows error message in UI; logs full details. |

### State persistence & UI synchronisation

| Source | Presenter hand-off | Model / State target | Notes |
| --- | --- | --- | --- |
| **Model → State serialization** | `model.to_dict()` | JSON-serializable dict | Captures test rows, time-series, temperature, metadata, and last source path. |
| **Disk → State restoration** | `presenter.restore_state(state_dict)` | Calls `model.reset()` then rehydrates via setters | Presenter handles version upgrade/downgrade logic. |
| **Model → State change events (time-series/test rows/temp)** | `presenter.refresh_view()` | Pulls `model.get_state()` & `model.build_time_series_rows()` | Presenter updates tables, plot, and summary labels after any mutation (manual edit, CSV load, reset). |
| **Model → Plot data** | `presenter.update_plot()` | `model.list_measurements()` / `do2_plot.build_do2_time_series()` | Triggered after state changes; keeps matplotlib figure in sync. |
| **Model → Spec override validation** | `presenter.handle_spec_override_error(mismatch)` | N/A | Presenter compares user-entered spec min/max against DS-50 defaults and raises user-visible error dialogs while logging details (planned). |

### persistence state

- `schema_version`: Marks the serialization contract version for forward/ backward migration checks in the presenter.
- `oxygen_data`: Minute-indexed dissolved O₂ readings stored as strings → float mappings; presenter normalizes UI edits before persistence.
- `temperature_c`: Shared bath temperature (optional float). Absent, the UI shows an empty field.
- `test_rows`: Ordered list of table rows, including DS-50 defaults, overrides, pass/fail, and measured values. Drives table + report regeneration.
- `serial_number`, `tester_name`, `test_location`, `test_date`: Metadata captured in the header; presenter ensures basic formatting before save.
- `source_path`: Last CSV import location to pre-seed future imports (optional).

## 5. Dependencies
- PDF generation library (QPdfWriter/QPrinter)
- Matplotlib or similar for graph plotting
- NumPy for data handling
## 6. Performance Budget
- Tab first show: ≤200 ms to render initial UI (no Matplotlib/NumPy import on init; lazy‑load on “Generate Report”).
- Generate report (PDF with 1 table + 1 time‑series chart, up to 1,000 points): ≤2.0 s on typical dev hardware; ≤4.0 s at 10,000 points. Runs off the UI thread.
- UI responsiveness: no single UI‑thread task >16 ms; progress indicator visible during generation.
- Memory: peak additional memory for generation ≤150 MB; steady‑state after completion ≤75 MB above baseline.
- PDF size: ≤2 MB for typical report; ≤5 MB at 10k points.
- Startup neutrality: does not increase app startup or first window paint; heavy libs are not imported at app start.
- How to measure:
  - Log `on_first_show_ms`, `report_generate_ms`, `peak_mem_mb`; assert in tests or CI smoke.
## 7. Non-Goals
- No real‑time acquisition or streaming.
- No historical storage or DB integration.
- No advanced analytics beyond chart + basic summaries.
- No custom multi‑page or highly themed layouts.
- No network/cloud export or service calls.
## 8. Acceptance Criteria
- Flag controls visibility; tab hidden when disabled.
- Required fields validated; “Generate” disabled until valid.
- Background generation with responsive UI and status feedback.
- PDF includes the specified tables and chart; values match inputs.
- Save dialog works; errors surfaced in tab; full details in logs.
- Meets performance budget; state persists across sessions.
- Matplotlib/NumPy loaded only on generation.
## 9. Rollout Plan
- Flag: `dissolved_o2`
- Default: off in `dev` and prod; toggle via config or CLI (`--enable-do-tab`)
- CI runs with flag off and on