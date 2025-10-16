# Plan: Add a New Tab Cleanly, Safely, and Reversibly

**Feature Branch:** `feat/dissolved-ox-tab`
**Status:** 🟡 In Progress - Core UI & Data Layer Complete

---

## 📋 Progress Checklist

- [x] **Step 1:** Frame the work (feature brief written: `dissolved-ox-plan.md`)
- [x] **Step 2:** Integration strategy (Tab Registry implemented)
- [x] **Step 3:** Module boundary (`dissolved_o2_tab/` with MVP architecture)
- [x] **Step 4:** Data flow traced (inputs/outputs defined in plan)
- [x] **Step 5:** Threading planned (QThreadPool approach documented)
- [x] **Step 6:** Instrumentation (console output for errors, ready for logging)
- [ ] **Step 7:** Accessibility & keyboard shortcuts
- [x] **Step 8:** Tracer-bullet skeleton (tab registered, loadable, UI built)
- [ ] **Step 9:** Tests (unit tests for model/presenter)
- [x] **Step 10:** Performance (lazy loading, no heavy imports at init)
- [x] **Step 11:** Error handling (try-except in presenter, validation in model)
- [ ] **Step 12:** Persistence (save/restore state methods)
- [x] **Step 13:** Security (input validation at presenter boundary)
- [ ] **Step 14:** Documentation (`README.md` for tab)
- [ ] **Step 15:** CI/packaging (test with flag on/off)
- [ ] **Step 16:** Definition of Done
- [ ] **Step 17:** Merge & post-merge

**👉 CURRENT LOCATION:** Core data entry & reset complete - **MONDAY: Chart rendering → PDF generation**

---

## Implementation Log

### ✅ Completed
- **Model layer:** Metadata dataclass, time-series storage, test rows, CSV import/export, validation (fixed oxygen validation bug)
- **View layer:** Full UI with metadata form, test table (hierarchical, fixed height), time-series table (center-aligned), chart placeholder, collapsible console
- **Presenter layer:** Signal wiring, metadata handlers, test table editing (Pass/Fail combos), CSV import/export, error handling
- **Time series editing:** Cell change handler with validation, clear on empty, console feedback
- **Reset button:** Confirmation dialog, clears all data, refreshes UI
- **Architecture:** TYPE_CHECKING circular import fix, proper MVP separation
- **UX polish:**
  - Dropdown combos for Pass/Fail
  - Table column stretching
  - Side-by-side layout for time-series/chart
  - Center-aligned oxygen values
  - Test table locked to 7-row height
  - Console collapsible with toggle

### 🚧 In Progress
- ⏸️ **Chart rendering** - Ready to start Monday (integrate matplotlib figure)
- ⏸️ **PDF report generation** - After chart complete

### ⏳ Not Started
- State save/restore
- Unit tests
- Documentation

---

## 1) Frame the work before touching code ✅

**Executed:**
* ✅ Feature brief written: `dissolved-ox-plan.md` with purpose, user flow, inputs/outputs, performance budget, non-goals
* ✅ Acceptance criteria defined (tab init <200ms, no UI blocking, error surfacing)
* ✅ Visibility strategy: feature flag `dissolved_o2` defaults to `False` in `testpad_main.py:202`

## 2) Decide the integration strategy ✅

**Executed:**
* ✅ Tab Registry already existed at `ui/tabs/registry.py`
* ✅ Added new `TabSpec` to `TABS_SPEC` list with feature flag
* ✅ Used existing `BaseTab` interface (provides `save_state`, `restore_state`, `on_show`, `on_close`)
* ✅ Registry uses lazy loading via `importlib.import_module()`

**Files modified:**
- `ui/tabs/registry.py`: Added dissolved O2 tab spec with `feature_flag="dissolved_o2"`
- `testpad_main.py`: Feature flag defined, tab filtered via `enabled_tabs()`

## 3) Carve out a clean module boundary ✅

**Executed:**
* ✅ Created MVP architecture in `ui/tabs/dissolved_o2_tab/`
* ✅ Separation of concerns: Model (data/validation), Presenter (coordination), View (UI)
* ✅ Fixed circular import using `TYPE_CHECKING` pattern
* ✅ No cross-tab dependencies - fully isolated module

### Actual structure implemented

```
src/testpad/ui/tabs/dissolved_o2_tab/
  ├── __init__.py              # Re-exports DissolvedO2Tab
  ├── model.py                 # Data layer: validation, CSV I/O, state
  ├── presenter.py             # Coordination: signals, model updates, threading
  ├── view.py                  # UI layer: QWidgets, layouts, tables
  ├── do2_plot.py              # Matplotlib helper for time-series chart
  ├── state_schema.json        # Persistence schema definition
  ├── widgets/
  │   └── __init__.py          # Custom widgets (future)
  └── resources/
      └── README.md            # Static assets placeholder
```

## 4) Trace the data flow early

* Specify input sources the tab relies on and the exact types or schemas.
* Specify outputs it produces and how they are consumed elsewhere.
* Define state persistence keys and their default values. Version the state with a tiny integer in `state_schema.json`.

## 5) Plan for threading and responsiveness

* Any compute or IO must go through a `TaskRunner` that uses `QThreadPool`. Presenter subscribes to task progress and completion. UI thread only updates widgets.
* Set a time budget. If a single operation might exceed it, chunk or stream results.

## 6) Instrumentation and observability

* Add structured logging context: `component=tab:new_feature`, include `operation`, `elapsed_ms`, `inputs_digest`.
* Emit user-visible status events: idle, running, success, warning, error.
* If you have telemetry, increment counters for tab open, task start, task cancel, failures.

## 7) Accessibility, keyboard, and UX hygiene

* Assign an access key to the tab, define keyboard shortcuts for primary actions, and ensure tab order makes sense.
* Provide inline error text and a “copy details” action for stack traces.
* Make the tab icon monochrome SVG to match existing style.

## 8) Build a tracer-bullet skeleton ✅

**Executed:**
* ✅ Tab registered in `registry.py` with `feature_flag="dissolved_o2"`
* ✅ Full UI implemented in `view.py`:
  - Metadata section (tester, date, location, serial)
  - Test results table (7 rows, hierarchical with header row for re-circulation test)
  - Time-series table (11 rows for minutes 0-10) with chart placeholder side-by-side
  - Action buttons (Import CSV, Export CSV, Generate Report, Reset)
  - Collapsible console output section
* ✅ Presenter wired with functional handlers:
  - Metadata field changes → model updates
  - Test table editing with Pass/Fail dropdown combos
  - CSV import/export fully working
  - Temperature input with validation
  - Error handling with console feedback

## 9) Tests before behavior

* Unit tests: model transforms, serialization, and any calculations.
* Presenter tests: signal in, effect out, no GUI required.
* Integration smoke: app boots with tab enabled, tab can open, save, restore.
* If you have GUI tests, add one golden screenshot at default DPI. Keep it brittle only where visual regressions matter.

## 10) Performance checks

* Time `on_first_show` and first background task. Capture baseline in logs so you can compare after optimizations.
* Cap memory growth by using weak refs to large shared data or slicing views over arrays.

## 11) Error handling policy

* All background tasks return a typed result or a rich error object, never throw into the UI thread.
* UI surfaces concise messages; logs capture the full traceback and context.

## 12) Persistence and migration

* Implement `save_state` and `restore_state` on the tab with versioned schema.
* If schema changes later, write a small migrator keyed on `schema_version`.

## 13) Security and data hygiene

* Validate all file paths and user inputs at the presenter boundary.
* Redact sensitive fields in logs. Avoid writing raw data dumps unless the user explicitly exports.
* Flag spec min/max overrides that deviate from factory defaults per DS-50 model; surface user-facing errors while allowing deliberate overrides.

## 14) Docs and developer ergonomics

* Add a short `README.md` under `tabs/new_feature` describing public signals, state keys, and typical usage.
* Update top-level `CONTRIBUTING.md` with how to add future tabs via the registry.
* Add an ASCII map of the registration points in `registry.py` so new devs do not spelunk.

### Registration touchpoints

```
main_window.py         -> asks TabRegistry.list_enabled()
tabs/registry.py       -> holds metadata, flag gating, factory callables
tabs/base_tab.py       -> ITab, common save/restore helpers
tabs/new_feature/*     -> the actual module
```

## 15) CI, packaging, and release steps

* CI: run unit tests, lint, type checks with the feature flag both off and on.
* Artifacts: ensure resources are added to qrc or packaging spec so icons and qss load.
* Release notes: add a single line under “Added” with the flag name (`dissolved_o2`) and how to enable it in `dev`.
* Rollback plan: keeping it behind a flag makes rollback trivial. Also keep a small git tag before merge.

## 16) Definition of Done

* Meets all acceptance criteria.
* No UI thread stalls during heavy operations.
* State save/restore verified.
* Logging is structured and useful for RCA.
* Tests green, coverage for model and presenter logic, smoke test for tab init.
* Feature flag default off on `dev` until QA signs off, then flip default to on.

## 17) Merge and post-merge hygiene

* Squash to a readable commit history that tells a story: registry, skeleton, tests, behavior, polish.
* After merge to `dev`, enable the flag for internal builds and collect feedback for one cycle before promoting to `main`.

If your current codebase is still a monolith, this plan lets you introduce just enough structure to keep the new tab isolated without derailing other work. Next logical extension is to migrate one existing tab into the same pattern, which gives you a consistent skeleton for future features.

---

## 🎯 Next Steps (Priority Order)

### Immediate (Core Functionality)
1. ✅ ~~**Time Series Editing**~~ - COMPLETE: Handler implemented with validation, clear-on-empty, console feedback
2. ✅ ~~**Reset Button**~~ - COMPLETE: Confirmation dialog, model reset, UI refresh
3. **Chart Rendering** ⭐ START MONDAY - Integrate matplotlib figure into chart widget:
   - Import matplotlib in presenter (lazy load - only when needed)
   - Use `do2_plot.build_do2_time_series()` to generate figure
   - Embed figure in `_chart_widget` using FigureCanvas from matplotlib.backends.backend_qt5agg
   - Update chart when: time series data changes, CSV imported, reset clicked
   - Handle edge case: empty data (show empty/placeholder chart)
4. **PDF Report Generation** - Implement with QThread for background processing:
   - Create report layout (metadata + tables + chart)
   - Use QPdfWriter or QTextDocument → PDF
   - Add progress feedback during generation
   - Save dialog on completion

### Polish & Robustness
5. **State Persistence** - Implement `save_state()` and `restore_state()` methods
6. **Error Dialogs** - Replace console messages with QMessageBox for critical errors
7. **Input Validation UI** - Visual feedback for invalid entries (red borders, tooltips)

### Testing & Documentation
8. **Unit Tests** - Model validation, CSV parsing, state serialization
9. **Integration Tests** - Tab loading, signal flow, file I/O
10. **README.md** - Document tab usage, data format, extension points

### Pre-Merge
11. **Re-enable all tabs** in `registry.py` (currently commented for dev speed)
12. **Performance profiling** - Verify <200ms tab load, <2s report generation
13. **Code review** - Address feedback, refactor if needed
14. **Update CONTRIBUTING.md** - Document tab development pattern for future devs

---

## 📝 Session Summary & Monday Prep

### What We Accomplished This Session
- ✅ Built complete MVP architecture (Model-View-Presenter)
- ✅ Implemented all data entry functionality (metadata, test table, time series)
- ✅ CSV import/export working
- ✅ Reset functionality with confirmation
- ✅ Fixed circular import issues (TYPE_CHECKING pattern)
- ✅ Polished UI (dropdowns, alignment, fixed heights, collapsible console)
- ✅ Created reusable templates for future features

### Ready for Monday
**Files to work with:**
- `presenter.py` - Will add chart update logic
- `view.py` - Chart widget already has placeholder
- `do2_plot.py` - Helper function already exists

**What chart rendering needs:**
1. Import `FigureCanvas` from `matplotlib.backends.backend_qt5agg`
2. Create canvas from figure returned by `build_do2_time_series()`
3. Add canvas to `_chart_widget` layout
4. Call chart update after: data changes, CSV import, reset

**Estimated time:** 30-45 minutes for chart rendering

### Known Issues / Tech Debt
- ❌ Other tabs still commented out in `registry.py` (remember to re-enable before merge)
- ❌ Console shows messages but no proper error dialogs yet
- ❌ No state persistence (data lost on tab close)
- ❌ No unit tests yet

### Performance Check
- ✅ Tab loads quickly (no matplotlib imported on init)
- ✅ UI responsive (all heavy ops planned for background)
- ⏳ Need to verify: chart render time, PDF generation time
