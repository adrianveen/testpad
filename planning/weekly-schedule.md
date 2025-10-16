# Work Schedule: Week of October 6-10, 2025

## Overview
This week focuses on completing the Dissolved Oxygen tab feature and beginning code quality improvements. The DO tab is currently ~70% complete with core data entry functionality working. Primary goals are finishing chart rendering, PDF generation, testing, and documentation before merge.

---

## Monday, October 6

### 8:00 AM - 9:00 AM
🍳 **Breakfast & Morning Prep**

### 9:00 AM - 11:00 AM
**DO Tab: Chart Rendering** ⭐ HIGH PRIORITY
- Import matplotlib components (lazy load in presenter)
- Integrate `do2_plot.build_do2_time_series()` helper
- Embed FigureCanvas into `_chart_widget`
- Wire chart updates: data changes, CSV import, reset
- Test edge cases (empty data, single point, full range 0-10 minutes)

**Files:** `presenter.py`, `view.py`, `do2_plot.py`
**Estimated:** 30-45 minutes implementation + 45 minutes testing/polish

### 11:00 AM - 12:00 PM
📞 **Interview Intro Call**

### 12:00 PM - 1:00 PM
🥗 **Lunch Break**

### 1:00 PM - 3:30 PM
**DO Tab: PDF Report Generation (Part 1)**
- Design report layout (metadata header, test table, time-series table, chart)
- Research QPdfWriter vs QTextDocument approach
- Implement basic PDF structure generation
- Test with sample data

**Files:** Create `pdf_generator.py` in `dissolved_o2_tab/`
**Goal:** Working PDF export with placeholder content

### 3:30 PM - 4:30 PM
**DO Tab: PDF Report Generation (Part 2)**
- Integrate actual data from model
- Format tables for PDF layout
- Embed matplotlib chart as image
- Handle page breaks and margins

### 4:30 PM - 5:00 PM
**Wrap-up & Documentation**
- Test full PDF generation workflow
- Document any issues/blockers
- Commit progress (`feat: Add chart rendering and PDF generation skeleton`)

---

## Tuesday, October 7

### 8:00 AM - 9:00 AM
🍳 **Breakfast & Email Review**

### 9:00 AM - 11:30 AM
**DO Tab: PDF Generation - Background Threading**
- Implement QThread or QThreadPool for background generation
- Add progress indicator/status feedback to UI
- Handle cancellation and error states
- Test with various data sizes (empty, small, 1000+ points)

**Files:** `presenter.py`, `view.py`, create `tasks.py` for background workers
**Goal:** Non-blocking PDF generation with user feedback

### 11:30 AM - 12:00 PM
**DO Tab: Error Handling Polish**
- Replace console messages with QMessageBox for critical errors
- Add visual feedback for invalid inputs (red borders, tooltips)
- Test error scenarios (invalid CSV, missing data, IO errors)

### 12:00 PM - 1:00 PM
🥗 **Lunch Break**

### 1:00 PM - 3:00 PM
**DO Tab: State Persistence**
- Implement `save_state()` method (serialize to dict)
- Implement `restore_state()` method (deserialize from dict)
- Use `state_schema.json` for versioning
- Test: enter data → close tab → reopen → verify data restored

**Files:** `view.py`, `presenter.py`, `model.py`
**Reference:** See BaseTab interface requirements

### 3:00 PM - 5:00 PM
**DO Tab: Unit Tests (Part 1)**
- Test model validation logic (`_validate_minute`, `_validate_oxygen`, `_validate_temperature`)
- Test CSV parsing (`load_from_csv`, `export_csv`)
- Test state serialization (`to_dict`, schema compliance)
- Test measurement storage (`set_measurement`, `clear_measurement`, `reset`)

**Create:** `tests/ui/tabs/dissolved_o2_tab/test_model.py`
**Goal:** >80% model coverage

---

## Wednesday, October 8

### 8:00 AM - 9:00 AM
🍳 **Breakfast & Code Review Prep**

### 9:00 AM - 11:00 AM
**DO Tab: Unit Tests (Part 2)**
- Test presenter signal handling (mocked model and view)
- Test CSV import/export flows
- Test error handling pathways
- Test reset confirmation logic

**Create:** `tests/ui/tabs/dissolved_o2_tab/test_presenter.py`

### 11:00 AM - 12:00 PM
**DO Tab: Integration Tests**
- Test tab loading with feature flag on/off
- Test full workflow: import CSV → edit data → generate PDF → save
- Smoke test: app boots with tab enabled
- Performance check: tab load <200ms, PDF generation <2s

**Create:** `tests/integration/test_dissolved_o2_tab.py`

### 12:00 PM - 1:00 PM
🥗 **Lunch Break**

### 1:00 PM - 2:30 PM
**DO Tab: Documentation**
- Write `README.md` for `dissolved_o2_tab/`:
  - Overview of MVP architecture
  - Public signals and methods
  - State schema documentation
  - CSV format specification
  - Extending the tab (adding test rows, custom validations)

**Create:** `src/testpad/ui/tabs/dissolved_o2_tab/README.md`

### 2:30 PM - 4:00 PM
**DO Tab: Pre-Merge Checklist**
- Re-enable all tabs in `registry.py` (currently commented)
- Run full test suite
- Lint and type check with mypy
- Profile tab load time and memory usage
- Test with feature flag both on and off in CI

### 4:00 PM - 5:00 PM
**Code Review & Cleanup**
- Self-review all changes
- Address any TODO comments
- Clean up debug prints
- Update CHANGELOG with new feature
- Prepare PR description

---

## Thursday, October 9

### 8:00 AM - 9:00 AM
🍳 **Breakfast & Planning**

### 9:00 AM - 11:00 AM
**Code Quality: BaseGraph Abstract Class** (Section 6.1, 6.3, 6.4)
- Create `src/testpad/core/graphs/base_graph.py`
- Define abstract methods: `prepare_data()`, `plot()`, `get_canvas()`
- Implement shared functionality: figure creation, canvas wrapping, resize handling
- Document the base class interface

**Goal:** Foundation for eliminating 500+ lines of duplicate code

### 11:00 AM - 12:00 PM
**Code Quality: Refactor BurninGraph**
- Make `BurninGraph` inherit from `BaseGraph`
- Move data loading to `prepare_data()`
- Move plotting logic to `plot()`
- Test: ensure existing burn-in tab still works

### 12:00 PM - 1:00 PM
🥗 **Lunch Break**

### 1:00 PM - 3:00 PM
**Code Quality: Refactor HydrophoneGraph**
- Make `HydrophoneGraph` inherit from `BaseGraph`
- Implement required abstract methods
- Test: ensure existing hydrophone tab still works

### 3:00 PM - 4:30 PM
**Code Quality: Centralized Color Configuration** (Section 2.1)
- Create `src/testpad/utils/theme_colors.py`
- Define `ThemeColors` class with named constants
- Update `BurninGraph` to use `ThemeColors.AXIS_A_COLOR`
- Update `HydrophoneGraph` to use `ThemeColors.HYDROPHONE_COLOR`

**Goal:** Single source of truth for color palette

### 4:30 PM - 5:00 PM
**Testing & Documentation**
- Test graph refactorings
- Update any affected tests
- Document `BaseGraph` usage in CONTRIBUTING.md

---

## Friday, October 10

### 8:00 AM - 9:00 AM
🍳 **Breakfast & Week Review**

### 9:00 AM - 11:00 AM
**Code Quality: File Dialog Abstraction** (Section 6.1)
- Create `src/testpad/utils/file_dialogs.py`
- Implement `FileDialogService` class:
  - `select_file(title, filter, default_path)` → str | None
  - `select_files(title, filter)` → List[str]
  - `select_directory(title, default_path)` → str | None
  - `save_file_dialog(title, filter, default_name)` → str | None
- Test helper methods

**Goal:** Reusable abstraction to eliminate ~300 lines of duplicate code

### 11:00 AM - 12:00 PM
**Code Quality: Update BurninTab to use FileDialogService**
- Replace `openFileDialog()` with `FileDialogService.select_file()`
- Test file selection workflow
- Verify no regressions

### 12:00 PM - 1:00 PM
🥗 **Lunch Break**

### 1:00 PM - 3:00 PM
**Code Quality: Fix BaseTab Inheritance** (Section 6.3)
- Update `BurninTab(QWidget)` → `BurninTab(BaseTab)`
- Implement `save_state()` override (burnin_file, checkboxes)
- Implement `restore_state()` override
- Test state persistence

**Goal:** Fix broken polymorphism for 1/11 tabs as proof of concept

### 3:00 PM - 4:30 PM
**DO Tab: Final Polish & Merge Prep**
- Address any PR feedback from code review
- Final testing pass
- Update feature flag documentation
- Squash commits into logical story
- Final CI check (all tests green, lint passing)

### 4:30 PM - 5:00 PM
**Week Wrap-up**
- Review week accomplishments
- Update `code-quality-improvements.md` with completed items (✅)
- Update `dissolved-ox-implementation.md` status
- Plan next week priorities
- Commit final changes

---

## Success Metrics

### Dissolved Oxygen Tab (Primary Goal)
- ✅ Chart rendering working
- ✅ PDF generation functional (background thread)
- ✅ State persistence implemented
- ✅ Unit tests >80% coverage
- ✅ Documentation complete
- ✅ Ready for merge review

### Code Quality Improvements (Secondary Goal)
- ✅ BaseGraph created (2-3 graphs refactored)
- ✅ ThemeColors centralized
- ✅ FileDialogService created
- ✅ 1 tab fixed to inherit from BaseTab

### Time Allocation
- **DO Tab completion:** ~70% of week (Mon-Wed + Fri afternoon)
- **Code quality:** ~25% of week (Thu + Fri morning)
- **Testing & docs:** ~15% throughout week

---

## Notes & Contingencies

**If DO Tab finishes early (Wednesday EOD):**
- Accelerate code quality improvements
- Start MVP migration for Vol2PressTab (largest monolithic tab at 24.5 KB)

**If PDF generation takes longer than expected:**
- Timebox to Wednesday EOD
- Document remaining work as follow-up tasks
- Focus on getting MVP merged with chart rendering only

**Risks:**
- ⚠️ PDF generation background threading might be complex (buffer extra time Tuesday)
- ⚠️ State persistence schema versioning needs careful design
- ⚠️ Interview call might run over (buffer Monday afternoon)

**Opportunities:**
- DO tab serves as template for future feature development
- BaseGraph refactoring benefits all future graph features
- Code quality improvements reduce technical debt incrementally

---

## Weekend Prep (Optional)
- Review matplotlib documentation for PDF embedding best practices
- Research QTextDocument vs QPdfWriter tradeoffs
- Read up on Qt threading patterns (QThread vs QThreadPool)
