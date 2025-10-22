# Plan: Add a New Tab Cleanly, Safely, and Reversibly

**Feature Branch:** `feat/dissolved-ox-tab`
**Status:** 🟡 Pre-Merge Phase - Core features complete, needs logging, tests, and code review

---

## 📋 Progress Checklist

- [x] **Step 1:** Frame the work (feature brief written: `dissolved-ox-plan.md`)
- [x] **Step 2:** Integration strategy (Tab Registry implemented)
- [x] **Step 3:** Module boundary (`degasser_tab/` with MVP architecture)
- [x] **Step 4:** Data flow traced (inputs/outputs defined in plan)
- [x] **Step 5:** Threading planned (QThreadPool approach documented, operations fast enough to skip)
- [ ] **Step 6:** Instrumentation (console output exists, structured logging needed)
- [ ] **Step 7:** Accessibility & keyboard shortcuts
- [x] **Step 8:** Tracer-bullet skeleton (tab registered, loadable, UI built)
- [ ] **Step 9:** Tests (unit tests for model/presenter)
- [x] **Step 10:** Performance (lazy loading, no heavy imports at init)
- [x] **Step 11:** Error handling (try-except in presenter, validation in model)
- [ ] **Step 12:** Persistence (skeleton exists with to_dict/from_dict, needs verification)
- [x] **Step 13:** Security (input validation at model boundary with type safety)
- [x] **Step 14:** Documentation (implementation plan maintained, inline docs complete)
- [ ] **Step 15:** CI/packaging (test with flag on/off)
- [ ] **Step 16:** Definition of Done (missing: logging, tests, persistence verification)
- [ ] **Step 17:** Merge & post-merge

**👉 CURRENT LOCATION:** All core functionality complete (83 commits on branch). Working tree clean. Ready for: structured logging, unit tests, code review, and merge preparation.

---

## Implementation Log

### ✅ Completed
- **Model layer:** Metadata dataclass, time-series storage, test rows, CSV import/export, validation (fixed oxygen validation bug)
- **View layer:** Full UI with metadata form, test table (hierarchical, fixed height), time-series table (center-aligned), live chart rendering, collapsible console
- **Presenter layer:** Signal wiring, metadata handlers, test table editing (Pass/Fail combos), CSV import/export, error handling, chart update orchestration
- **Time series editing:** Cell change handler with validation, clear on empty, console feedback
- **Reset button:** Confirmation dialog, clears all data, refreshes UI
- **Architecture:** TYPE_CHECKING circular import fix, proper MVP separation
- **ViewState pattern:** ✅ COMPLETE
  - Created `view_state.py` with immutable `DegasserViewState` dataclass
  - Presenter builds ViewState from Model and passes to View
  - View.update_view() accepts ViewState and renders UI
  - Clean unidirectional data flow: Model → ViewState → View
  - No direct model access from View layer
- **Type safety improvements:** ✅ COMPLETE (commits 9ec8b32, 828265e)
  - View.get_time_series_cell_value() returns `float | None` instead of `str`
  - Type conversion happens at View boundary (earliest possible point)
  - Proper None handling with item existence checks
  - Presenter updated to handle typed values (`if value is None` instead of `if value == ""`)
  - Leverages type narrowing for clean code without explicit casts
- **MVP architecture refinement:** ✅ COMPLETE (commit 828265e)
  - Presenter no longer directly manipulates view widgets
  - All view updates go through ViewState pattern
  - Clean separation: Presenter coordinates, View renders
  - Removed widget-touching code from presenter handlers
- **Chart rendering:** ✅ COMPLETE
  - Custom `TimeSeriesChartWidget` (reusable QWidget)
  - Matplotlib Figure/Axis/Canvas integration
  - Real-time updates with efficient `ax.clear()` + `canvas.draw()` pattern
  - Temperature displayed in chart title when measured
  - Relocated from `ui/widgets/` to `degasser_tab/chart_widgets.py` for better encapsulation (commit d5e6c0b)
  - Uses constants from `config/plotting.py`
- **Pure plotting functions:** ✅ COMPLETE
  - Created `plotting.py` with Qt-independent matplotlib functions
  - `make_time_series_figure()` - Create Figure from data
  - `plot_time_series_on_axis()` - Plot on existing Axis (for widgets)
  - `save_figure_to_temp_file()` - Save Figure to temp PNG for PDF embedding
  - `normalize_time_series_data()` - Convert dict/list to sorted tuples
  - Clean separation: plotting.py (pure functions) vs chart_widgets.py (Qt integration)
- **PDF report generation:** ✅ COMPLETE (commits f244a15, 6c7ebbe, 413e7c1, 742c12e, 3290528, 5a42b16)
  - Full implementation with fpdf library (303 lines in generate_pdf_report.py)
  - `report_layout.py` - Layout configuration with dataclasses (150 lines)
  - Metadata section with 2x2 grid layout
  - Test results table with actual data population (commit 742c12e)
  - Time series table with data
  - Embedded matplotlib chart via temporary PNG file (300 DPI)
  - SVG logo support (commit 5a42b16)
  - Error handling with user-friendly QMessageBox dialogs
  - Saves to DEFAULT_EXPORT_DIR with proper file permissions handling
  - All formatting magic numbers moved to report_layout.py (commit 5a42b16)
- **Configuration architecture:** ✅ COMPLETE (commit 15ce9db)
  - Created `testpad/config/` module for app-wide constants and defaults
  - Created `degasser_tab/config.py` with DS-50 specifications (93 lines)
  - Separated constants (physical laws) from defaults (user-configurable)
  - Moved `utils/plot_config.py` → `config/plotting.py`
  - Established pattern for future tab-specific configurations
  - Eliminated magic numbers (commit 58e0470 "last magic num fixed")
- **Temperature input:** Checkbox + QLineEdit pattern for optional temperature
  - Checkbox controls visibility/enabled state
  - QLineEdit allows empty state (None)
  - Chart title updates dynamically
  - Real-time updates with `textChanged` signal
  - `hasFocus()` guard prevents interrupting user typing
- **UX polish:**
  - Dropdown combos for Pass/Fail
  - Table column/row stretching (responsive design)
  - Side-by-side layout for time-series/chart
  - Center-aligned oxygen values
  - Test table locked to exact row height (no scrollbars)
  - Time series table expands to fill available space
  - Metadata form with right-aligned labels
  - Console collapsible with toggle
  - Clean import organization (commit 1d0fa63)

### 🚧 Pre-Merge Tasks
- **Structured logging** - Add logging with component context, operation tracking, elapsed time
- **Unit tests** - Model validation, CSV I/O, presenter logic
- **Code review** - Review for consistency, remove stale TODO comments
- **Persistence verification** - Test save_state/restore_state functionality
- **Performance measurement** - Verify tab load <200ms, PDF generation <2s

### ⏳ Deferred to Post-Merge
- Accessibility features (keyboard shortcuts, screen reader support)
- CI/packaging validation (test with flag on/off)
- QA sign-off on internal builds

---

## 1) Frame the work before touching code ✅

**Executed:**
* ✅ Feature brief written: `dissolved-ox-plan.md` with purpose, user flow, inputs/outputs, performance budget, non-goals
* ✅ Acceptance criteria defined (tab init <200ms, no UI blocking, error surfacing)
* ✅ Visibility strategy: feature flag `degasser_data` defaults to `False` in `testpad_main.py:202`

## 2) Decide the integration strategy ✅

**Executed:**
* ✅ Tab Registry already existed at `ui/tabs/registry.py`
* ✅ Added new `TabSpec` to `TABS_SPEC` list with feature flag
* ✅ Used existing `BaseTab` interface (provides `save_state`, `restore_state`, `on_show`, `on_close`)
* ✅ Registry uses lazy loading via `importlib.import_module()`

**Files modified:**
- `ui/tabs/registry.py`: Added degasser tab spec with `feature_flag="degasser_data"`
- `testpad_main.py`: Feature flag defined, tab filtered via `enabled_tabs()`

## 3) Carve out a clean module boundary ✅

**Executed:**
* ✅ Created MVP architecture in `ui/tabs/degasser_tab/`
* ✅ Separation of concerns: Model (data/validation), Presenter (coordination), View (UI)
* ✅ Fixed circular import using `TYPE_CHECKING` pattern
* ✅ No cross-tab dependencies - fully isolated module

### Actual structure implemented

```
src/testpad/ui/tabs/degasser_tab/
  ├── __init__.py                  # Re-exports DegasserTab
  ├── config.py                    # Tab-specific configuration: DS-50 specs, validation rules (100 lines)
  ├── model.py                     # Data layer: validation, CSV I/O, state, business logic (301 lines)
  ├── view_state.py                # ViewState pattern: immutable data transfer objects (34 lines)
  ├── presenter.py                 # Coordination: signals, model updates, ViewState building (327 lines)
  ├── view.py                      # UI layer: QWidgets, layouts, tables, ViewState rendering (785 lines)
  ├── chart_widgets.py             # Custom chart widget with matplotlib integration (40 lines)
  ├── plotting.py                  # Pure plotting functions (Qt-independent, 135 lines)
  ├── generate_pdf_report.py       # PDF report generation with fpdf (429 lines)
  ├── report_layout.py             # PDF layout configuration dataclasses (150 lines)
  └── widgets/                     # Custom UI widgets (5 lines)
```

**Total: 2,322 lines of well-structured, documented code across 10 modules**

### Configuration architecture pattern ✅

**Introduced in commit 15ce9db:** A centralized configuration system to improve maintainability and testability.

**Application-wide configuration** (`src/testpad/config/`):
```python
config/
  ├── __init__.py       # Public API for all config imports
  ├── constants.py      # Physical/scientific constants (ABSOLUTE_ZERO_C, etc.)
  ├── defaults.py       # User-facing defaults (DEFAULT_TEMPERATURE_C, etc.)
  └── plotting.py       # Matplotlib style configuration (moved from utils/)
```

**Tab-specific configuration** (example: `degasser_tab/config.py`):
- DS-50 test specifications and spec ranges
- CSV import column aliases
- Validation rules and limits
- Row-to-spec mappings for table construction

**Benefits:**
- Clear separation between constants (never change) and defaults (user-configurable)
- Tab-specific config isolated from business logic
- Easy to test: import config values directly rather than parsing from model
- Single source of truth for specifications and validation rules

**Pattern for future tabs:**
1. Create `tab_name/config.py` for tab-specific constants and validation rules
2. Import application-wide defaults from `testpad.config` as needed
3. Keep magic numbers and business rules out of model/presenter/view

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
* ✅ Tab registered in `registry.py` with `feature_flag="degasser_data"`
* ✅ Full UI implemented in `view.py`:
* ✅ Metadata section (tester, date, location, serial)
* ✅ Test results table (7 rows, hierarchical with header row for re-circulation test)
* ✅ Time-series table (11 rows for minutes 0-10) with chart placeholder side-by-side
* ✅ Action buttons (Import CSV, Export CSV, Generate Report, Reset)
* ✅ Collapsible console output section
* ✅ Presenter wired with functional handlers:
* ✅ Metadata field changes → model updates
* ✅ Test table editing with Pass/Fail dropdown combos
   - CSV import/export fully working
* ✅ Temperature input with validation
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
* Release notes: add a single line under “Added” with the flag name (`degasser_data`) and how to enable it in `dev`.
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

### ✅ Core Functionality Complete
1. ✅ **Time Series Editing** - Handler with validation, clear-on-empty, console feedback
2. ✅ **Reset Button** - Confirmation dialog, model reset, UI refresh
3. ✅ **Chart Rendering** - Custom widget with real-time matplotlib updates
4. ✅ **PDF Report Generation** - Complete with test data population (commits through 5a42b16)
   - fpdf-based report with SVG logo support
   - Metadata, test table with actual data, time series table, embedded chart
   - All magic numbers moved to configuration
5. ✅ **CSV Import/Export** - Full round-trip with flexible column aliases
6. ✅ **Data Entry** - Metadata form, test table with Pass/Fail combos, time series editing
7. ✅ **Navigation** - Cell navigation with keyboard overloads (commit 7f9de60)

### 🎯 Pre-Merge Tasks (Required)
1. **Structured Logging** - Add component context, operation tracking, elapsed_ms
2. **Unit Tests** - Model validation, CSV I/O, presenter signal handlers
3. **Code Review** - Clean up stale TODO (1 found in view.py:297), verify consistency
4. **State Persistence** - Verify save_state/restore_state works end-to-end
5. **Performance Measurement** - Benchmark tab load time, PDF generation time

### ⏳ Post-Merge Tasks
- Accessibility features (keyboard shortcuts, screen reader support)
- CI/packaging validation (test with feature flag on/off)
- QA sign-off on internal builds
- README.md for tab usage documentation
- Update CONTRIBUTING.md with tab development pattern

---

## 📝 Latest Session Summary (Current as of commit 7f9de60)

### Feature Branch Stats
- **83 commits** on feat/dissolved-ox-tab (diverged from main on 2025-10-02)
- **2,322 lines** of production code across 10 modules
- **Working tree:** Clean (no uncommitted changes)
- **Version:** testpad v1.11.0

### Major Accomplishments

#### 1. ViewState Pattern Implementation ✅
- Created `view_state.py` with immutable `DegasserViewState` dataclass
- Presenter builds ViewState from Model, passes to View
- View.update_view() renders from ViewState
- Achieved clean unidirectional data flow: Model → ViewState → View
- Eliminated direct model access from View layer

#### 2. Type Safety Improvements ✅ (Commits 9ec8b32, 828265e)
- **Problem solved:** View was returning strings, Model expected floats
- **Solution:** Type conversion at View boundary (earliest possible point)
- Changed `get_time_series_cell_value()` return type: `str` → `float | None`
- Added proper None handling with item existence checks
- Updated Presenter to handle typed values: `if value is None` (not `if value == ""`)
- Leveraged Python's type narrowing for clean code without explicit casts
- **Architecture principle applied:** "Parse Don't Validate" - convert at data source

#### 3. MVP Architecture Refinement ✅ (Commit 828265e)
- **"Presenter no longer touches view widgets"** - enforced separation of concerns
- All view updates now go through ViewState pattern
- Removed direct widget manipulation from presenter handlers
- Clean boundaries: Presenter coordinates, View renders
- Improved testability and maintainability

#### 4. PDF Report Generation ✅ COMPLETE (Commits f244a15 through 5a42b16)
- Created `generate_pdf_report.py` (429 lines) and `report_layout.py` (150 lines)
- ✅ PDF structure with fpdf library
- ✅ Metadata section (2x2 grid layout)
- ✅ Test results table with actual data population (commit 742c12e)
- ✅ Time series table with actual data from model
- ✅ Chart embedded as high-resolution PNG (300 DPI)
- ✅ SVG logo support (commit 5a42b16)
- ✅ All formatting magic numbers moved to report_layout.py
- ✅ Error handling with QMessageBox dialogs
- ✅ Saves to DEFAULT_EXPORT_DIR with proper file permissions

#### 5. Pure Plotting Functions ✅
- Created `plotting.py` - Qt-independent matplotlib functions (135 lines)
- `make_time_series_figure()` - Create standalone Figure from data
- `plot_time_series_on_axis()` - Plot on existing Axis (for widget updates)
- `save_figure_to_temp_file()` - Save Figure to temp PNG for PDF embedding
- `normalize_time_series_data()` - Normalize dict/list to sorted tuples
- **Clean separation:** plotting.py (pure) vs chart_widgets.py (Qt integration)

#### 6. Chart Widget Relocation ✅ (Commit d5e6c0b)
- Moved from `ui/widgets/chart_widgets.py` to `degasser_tab/chart_widgets.py`
- Better encapsulation - chart widget now part of degasser tab module
- Reduces coupling between tabs and shared widget library

#### 7. Configuration & Magic Number Elimination ✅ (Commit 58e0470)
- All magic numbers removed from code
- DS-50 specifications in `config.py` (93 lines)
- Application-wide config in `testpad/config/`
- Clear separation: constants (unchanging) vs defaults (user-configurable)

### Files Created/Modified Summary
**New files:**
- ✅ `view_state.py` - ViewState pattern (35 lines)
- ✅ `plotting.py` - Pure plotting functions (135 lines)
- ✅ `generate_pdf_report.py` - PDF generation (303 lines)
- ✅ `report_layout.py` - Layout configuration (103 lines)

**Major refactoring:**
- ✅ `view.py` - Type-safe cell value extraction, ViewState rendering
- ✅ `presenter.py` - ViewState building, no widget touching (295 lines)
- ✅ `model.py` - Business logic and validation (301 lines)
- ✅ `config.py` - Expanded to 93 lines with all DS-50 specs
- ✅ `chart_widgets.py` - Relocated to degasser_tab/

### Architecture Achievements
- ✅ **Clean MVP separation** - Model/View/Presenter boundaries enforced
- ✅ **Type safety** - Conversion at boundaries, no stringly-typed data
- ✅ **ViewState pattern** - Immutable state transfer, unidirectional flow
- ✅ **Pure functions** - Plotting logic separated from Qt/UI concerns
- ✅ **Configuration as code** - All specs and constants documented and typed
- ✅ **Error handling** - User-friendly messages, comprehensive try-except coverage

### Current Implementation Status
**Current state:** All core features complete, pre-merge tasks remaining

**What's working:**
- ✅ Full data entry (metadata, test table, time series)
- ✅ CSV import/export with flexible column aliases
- ✅ Real-time chart rendering with temperature display
- ✅ Type-safe data flow throughout the stack
- ✅ Input validation and error handling
- ✅ Reset functionality with confirmation
- ✅ PDF generation: complete report with all sections populated
- ✅ Cell navigation with keyboard overloads (commit 7f9de60)
- ✅ Custom delegate for units display in UI (commit 742c12e)

**Pre-merge requirements:**
1. Structured logging (component context, elapsed_ms tracking)
2. Unit tests (model, presenter, CSV I/O)
3. Code review (remove stale TODO at view.py:297)
4. State persistence verification
5. Performance benchmarking

**Deferred to post-merge:**
- Keyboard shortcuts and accessibility
- CI/packaging validation
- QA sign-off

### Technical Debt Status
- ✅ Magic numbers eliminated (commit 58e0470)
- ✅ Unused imports cleaned (commit 1d0fa63)
- ✅ Type safety issues resolved (commits 9ec8b32, 828265e)
- ✅ MVP architecture enforced (commit 828265e)
- ✅ All changes committed (working tree clean)
- ⚠️ No structured logging implemented
- ⚠️ No unit tests yet
- ⚠️ Stale TODO comment in view.py:297

---

## 💡 Lessons Learned & Architectural Insights

### What Went Well

#### 1. MVP Architecture Pattern
- **Insight:** Strict separation of Model/View/Presenter made refactoring easy
- **Example:** When we needed to add ViewState pattern, we only touched presenter.py and view.py
- **Benefit:** Model layer remained completely stable throughout UI changes
- **For future:** Always establish these boundaries early, even for "simple" features

#### 2. ViewState Pattern for UI Updates
- **Insight:** Immutable state objects eliminate entire classes of bugs
- **Example:** View can't accidentally mutate model state during rendering
- **Benefit:** Unidirectional data flow makes debugging trivial (follow the ViewState)
- **For future:** Use this pattern for all complex UI components

#### 3. Type Safety at Data Boundaries
- **Insight:** "Parse Don't Validate" - convert types at the earliest boundary
- **Example:** View returns `float | None` instead of `str`, eliminating downstream casting
- **Benefit:** Type checker catches errors at compile time, not runtime
- **For future:** Always convert types where data enters the system (View layer for UI input)

#### 4. Pure Functions for Plotting
- **Insight:** Separating matplotlib logic from Qt enables reuse and testing
- **Example:** `plotting.py` functions work in PDFs, widgets, and tests without modification
- **Benefit:** PDF generation and live widget updates share the same plotting code
- **For future:** Always separate framework-specific code (Qt) from business logic (matplotlib)

#### 5. Configuration as Code
- **Insight:** Centralizing constants/specs makes the codebase self-documenting
- **Example:** DS-50 specifications in `config.py` instead of scattered magic numbers
- **Benefit:** Single source of truth, easy to update, type-safe
- **For future:** Create `config.py` for every tab with specifications

### What Could Improve

#### 1. Type Safety Evolution
- **Issue:** Initial implementation returned strings, required later refactoring
- **Lesson:** Should have considered type boundaries from the start
- **For future:** Design data flow with type safety in mind during planning phase

#### 2. Testing Strategy
- **Issue:** Implemented features without accompanying tests
- **Lesson:** Tests deferred to post-merge due to time constraints
- **For future:** Write tests incrementally alongside features (TDD or test-soon)

#### 3. Git Commit Organization
- **Issue:** Some commits mixed multiple concerns (refactoring + features)
- **Lesson:** Should have kept commits more focused and atomic
- **For future:** Commit after each logical unit of work, use interactive rebase to organize

### Architectural Patterns Established

#### 1. Tab Module Structure
```
tab_name/
  ├── model.py           # Business logic, validation, state
  ├── view_state.py      # Immutable state transfer objects
  ├── presenter.py       # Coordination, ViewState building
  ├── view.py            # UI rendering from ViewState
  ├── config.py          # Specifications and constants
  └── [feature].py       # Feature-specific modules (plotting, reports, etc.)
```

#### 2. Data Flow Pattern
```
User Input → View (type conversion) → Presenter (coordination) → Model (validation)
Model State → Presenter (build ViewState) → View (render)
```

#### 3. Type Conversion Strategy
- **At View boundary:** Convert UI strings to typed values (`float | None`)
- **At Model boundary:** Validate and enforce business rules
- **Presenter:** Coordinates typed values, no conversion logic

#### 4. Error Handling Layers
- **View:** Displays user-friendly error messages (QMessageBox)
- **Presenter:** Catches exceptions, logs details, surfaces to View
- **Model:** Raises ValueError with descriptive messages for validation failures

### Technical Debt Incurred

#### 1. Unit Test Coverage
- **Debt:** No automated tests for model validation or presenter logic
- **Why incurred:** Prioritized working feature over test coverage
- **When to address:** Post-merge, before next feature
- **Mitigation:** Model.to_dict() and from_dict() skeleton makes tests easier to write later

#### 2. State Persistence
- **Debt:** Save/restore methods not implemented
- **Why incurred:** Core functionality was higher priority
- **When to address:** Post-merge, user-requested feature
- **Mitigation:** to_dict() provides serialization foundation

#### 3. Accessibility Features
- **Debt:** No keyboard shortcuts or screen reader support
- **Why incurred:** MVP focused on core functionality
- **When to address:** Based on user feedback
- **Mitigation:** Qt framework makes this relatively easy to add later

### Reusable Patterns for Future Tabs

1. **ViewState pattern** - Copy `view_state.py` structure
2. **Type-safe View methods** - Return typed values, not strings
3. **Pure plotting functions** - Separate from Qt widgets
4. **Configuration module** - Create `config.py` with all specs/constants
5. **Report generation** - Use `report_layout.py` pattern for configuration
6. **Error handling** - Model raises ValueError, Presenter shows QMessageBox

---
