# Implementation Plan: Burn-in PDF Report Generation

**Feature Branch:** `testpad/feat/generate-burnin-pdf`
**Status:** 🟡 In Progress
**Start Date:** 2025-10-28
**Target Completion:** 3 days from start

---

## 📋 Progress Checklist

- [x] **Step 1:** Frame the work (feature spec defined)
- [x] **Step 2:** Integration strategy (follows degasser pattern)
- [x] **Step 3:** Module boundary (simplified MVP architecture)
- [x] **Step 4:** Data flow traced (HDF5 → Stats → PDF)
- [ ] **Step 5:** Threading planned (not required - blocking operation acceptable)
- [ ] **Step 6:** Instrumentation (basic text display logging)
- [ ] **Step 7:** Accessibility & keyboard shortcuts (deferred)
- [x] **Step 8:** Tracer-bullet skeleton (button, presenter, report generator stubs exist)
- [ ] **Step 9:** Tests (manual testing only for v1)
- [ ] **Step 10:** Performance (not critical - runs on-demand)
- [ ] **Step 11:** Error handling (basic error dialogs)
- [ ] **Step 12:** Persistence (metadata only, via dialog)
- [ ] **Step 13:** Security (basic file validation)
- [ ] **Step 14:** Documentation (inline docstrings)
- [ ] **Step 15:** CI/packaging (feature flag enabled)
- [ ] **Step 16:** Definition of Done (see acceptance criteria below)
- [ ] **Step 17:** Merge & post-merge

**👉 CURRENT LOCATION:** Skeleton code exists (button, presenter stub, report generator stub). Next: Create core architecture (model, factory, plotting module) and wire components together.

---

## Implementation Log

### ✅ Completed
- **UI Button:** "GENERATE REPORT" button added with green styling
- **Presenter Skeleton:** Basic class structure with stubs
- **Report Generator Skeleton:** Header, title block, and layout config complete
- **Layout Config:** report_layout.py fully implemented with dataclasses

### 🚧 In Progress
- **Architecture Setup:** Need to create model.py, __init__.py factory, metadata dialog
- **Plotting Module:** Need pure matplotlib functions following degasser pattern
- **PDF Generation:** Stats table and graph embedding incomplete

### ⏳ Not Started
- **Signal Wiring:** Fix presenter method naming and connections
- **BurninStats Integration:** Make textbox parameter optional
- **Testing:** Manual validation of all features
- **Cleanup:** Remove scratch files, update .gitignore

---

## Detailed Implementation Steps

### Step 1: Frame the Work ✅

**Planned:**
* Add "GENERATE REPORT" button to Burnin Tab
* Generate PDF with metadata, stats tables, and 4 plots
* Follow degasser tab architecture (simplified MVP)
* 3-day timeline for fast turnaround

**Executed:**
* ✅ Feature goals defined
* ✅ Architecture decision: Simplified MVP with Model-Presenter pattern
* ✅ Plot selection: All 4 plots (main, separated, pos moving avg, neg moving avg)
* ✅ Metadata collection: Popup dialog on button click

**Files modified/created:**
- Planning document created

---

### Step 2: Integration Strategy ✅

**Planned:**
* Follow degasser tab pattern for consistency
* Use existing BurninStats and BurninGraph modules
* Register via factory function in registry.py
* Enabled via `burnin_tab` feature flag

**Executed:**
* ✅ Pattern identified: Model → View → Presenter with factory
* ✅ Reuse degasser's report layout approach
* ✅ Create plotting.py module (pure matplotlib functions)

**Files modified/created:**
- `registry.py`: Will change from `BurninTab` class to `create_burnin_tab` factory

---

### Step 3: Module Boundary 🚧

**Planned:**
* Simplified MVP pattern (Model + Presenter, no ViewState for v1)
* Clean separation: Model (data), View (Qt widgets), Presenter (logic)
* Plotting module provides pure matplotlib functions

**Module Structure:**

```bash
src/testpad/ui/tabs/burnin_tab/
  ├── __init__.py              # Factory: create_burnin_tab()
  ├── burnin_tab.py            # View (existing, minor updates)
  ├── model.py                 # NEW: BurninModel (file path + metadata)
  ├── burnin_presenter.py      # UPDATE: Full implementation
  ├── metadata_dialog.py       # NEW: QDialog for metadata input
  ├── plotting.py              # NEW: Pure matplotlib plotting
  ├── generate_pdf_report.py   # UPDATE: Complete stats/graphs
  └── report_layout.py         # ✅ Complete
```

**Executed:**
* ⏳ Need to create model.py, __init__.py, metadata_dialog.py, plotting.py

---

### Step 4: Data Flow ✅

**Data Sources:**
- HDF5 burn-in file: Error (counts) and Time (s) arrays
- User input: Metadata via dialog (Tested By, Test Name, Date, Serial Number)

**Flow:**

```bash
User selects HDF5 file → Model.set_burnin_file()
User clicks "GENERATE REPORT" → Metadata dialog appears
User enters metadata → Model.set_metadata_field()
Presenter.on_generate_report():
  1. Read HDF5 data (error, time arrays)
  2. Create BurninStats(burnin_file, textbox=None)
  3. Access stats: burnin_stats.positive_stats, negative_stats (tuples)
  4. Call plotting functions to get 4 matplotlib Figures
  5. Pass to GenerateReport(metadata, burnin_file, ...)
  6. GenerateReport.generate_report() creates PDF
  7. Save to DEFAULT_EXPORT_DIR
```

**Stats Tuple Format** (14 values each for positive/negative):

```python
(mean, median, std, var, max_val, min_val,
 q25, q75, skew, kurtosis,
 pct_above_thresh, pct_below_thresh, num_peaks, num_drops)
```

---

### Step 5: Threading & Responsiveness ⏳

**Planned:**

- PDF generation runs synchronously (blocking operation)
- Acceptable for v1 - generation is fast (<5 seconds)
- Future: Use QThread for long-running reports

**Executed:**

- ⏳ No threading required for v1

---

### Step 6: Instrumentation 🚧

**Planned:**

- Log success/error messages to text_display widget
- Basic error dialogs for user feedback

**Executed:**

- 🚧 Need to add logging in presenter

---

### Step 7: Accessibility ⏳

**Deferred to future work**

---

### Step 8: Tracer-Bullet Skeleton ✅

**Executed:**

- ✅ Button exists and renders
- ✅ Presenter skeleton with method stubs
- ✅ GenerateReport skeleton with header/title complete
- ⏳ Need to wire together and complete implementation

---

### Step 11: Error Handling 🚧

**Planned:**

- Validate burnin_file selected before showing dialog
- Handle dialog cancellation (silent abort)
- Try-except in presenter for generation errors
- User-friendly error messages via QMessageBox

**Error Scenarios:**

1. No file selected → Warning dialog
2. Invalid HDF5 file → Error message
3. Output directory not writable → Error message
4. User cancels metadata dialog → Silent abort

---

### Step 13: Security & Validation 🚧

**Planned:**

- Basic file validation (file exists and is readable)
- Not strict for v1 - accept any HDF5 file

---

### Step 16: Definition of Done ⏳

**Acceptance Criteria:**
- [ ] "GENERATE REPORT" button functional
- [ ] Metadata dialog collects 4 fields (Tested By, Test Name, Date, Serial)
- [ ] PDF generates with: header (logo), title block, metadata table
- [ ] Positive and negative error stats tables in PDF (14 stats each)
- [ ] All 4 plots in PDF: Page 1 (main + separated), Page 2 (pos/neg moving avg)
- [ ] Existing tab functionality unchanged (graphs, checkboxes, print stats)
- [ ] Auto-saves to DEFAULT_EXPORT_DIR
- [ ] Basic error handling (no file, generation errors)
- [ ] Success message appears in text display
- [ ] No temp files left after generation

---

## 🎯 Next Steps (Priority Order)

### Immediate (Critical Path)

1. **Create Model & Factory** ⭐ NEXT
   - Create `model.py` with BurninModel class
   - Create `__init__.py` with `create_burnin_tab()` factory
   - Update `registry.py` to use factory function

2. **Create Metadata Dialog**
   - Create `metadata_dialog.py` with QDialog
   - 4 input fields: Tested By, Test Name, Date (QDateEdit), Serial
   - Return dict on OK, None on cancel

3. **Create Plotting Module**
   - Create `plotting.py` with 4 functions:
     - `make_main_error_figure()` - combined error plot
     - `make_separated_errors_figure()` - pos/neg separated
     - `make_moving_avg_figure()` - moving avg plot
     - `save_figure_to_temp_file()` - save matplotlib to temp PNG
   - Follow degasser pattern (pure functions, no Qt)

4. **Complete Presenter Implementation**
   - Update `burnin_presenter.py`:
     - Add model parameter to __init__
     - Rename `_on_generate_report_clicked()` → `on_generate_report()`
     - Implement full report generation flow
     - Add file selection handler to update model
     - Add error handling and validation

5. **Complete PDF Generation**
   - Update `generate_pdf_report.py`:
     - Add burnin_file parameter to __init__
     - Implement `_build_stats_table()` - use stats tuples
     - Implement `_build_graphs()` - add 4 plots to PDF
     - Create helper `_add_plot_pair_to_page()` for side-by-side layout

### Polish & Robustness

6. **Wire View to Presenter**
   - Update `burnin_tab.py`:
     - Add model parameter to __init__
     - Fix signal connection (line 121): `on_generate_report` not `generate_report`
     - Update `openFileDialog()` to update model

7. **Make BurninStats Textbox Optional**
   - Update `burnin_stats.py`:
     - Change textbox parameter: `Optional[QTextBrowser] = None`
     - Check if textbox exists before calling display methods
     - Stats tuples still populated regardless

### Testing & Documentation

8. **Manual Testing**
   - Test existing functionality (graphs, stats, checkboxes)
   - Test new functionality (report generation, metadata dialog)
   - Validate PDF content (header, metadata, stats, 4 plots)
   - Test error scenarios (no file, cancel dialog, invalid file)

### Pre-Merge

9. **Cleanup**
   - Remove unused imports
   - Remove scratch files from tracking
   - Verify .gitignore covers planning/
   - Add docstrings to new classes/methods

---

## 🐛 Known Issues & Blockers

### Current Issues

- **Signal Connection Mismatch** (`burnin_tab.py:121`)
  - Line connects to `presenter.generate_report` (doesn't exist)
  - Should be `presenter.on_generate_report` (public method)
  - _Fix Plan:_ Rename method and update connection

- **BurninStats Requires Textbox** (`burnin_stats.py:12`)
  - Constructor requires QTextBrowser, but PDF generation doesn't have one
  - _Fix Plan:_ Make textbox optional parameter, check before display

### Technical Debt Incurred

- **Simplified MVP Pattern:** Using Model + Presenter without ViewState dataclass
  - _Why:_ 3-day timeline constraint
  - _When to Address:_ Future refactor when adding more features

- **BurninStats Integration:** Accessing tuple attributes directly instead of clean API
  - _Why:_ Fastest path to working solution
  - _When to Address:_ Create `get_stats_dict()` method in future refactor

- **No Threading:** Blocking PDF generation
  - _Why:_ Fast enough for v1, simpler implementation
  - _When to Address:_ If reports become large/slow

---

## 💡 Key Design Decisions

### Architecture
- **Simplified MVP:** Model + Presenter (no ViewState) for 3-day timeline
- **Reuse Degasser Pattern:** Plotting module with pure matplotlib functions
- **Factory Pattern:** Registry calls `create_burnin_tab()` factory function

### Plot Selection
- **All 4 Plots Included:**
  1. Main error (combined)
  2. Separated errors (pos/neg lines)
  3. Positive error w/ moving avg
  4. Negative error w/ moving avg
- **Layout:** 2 plots per page, side-by-side

### Metadata Collection
- **Popup Dialog:** Appears when clicking "GENERATE REPORT"
- **4 Fields:** Tested By, Test Name, Date, RK-300 Serial Number
- **Cancellation:** Silent abort (no error message)

### Stats Integration
- **Access Tuples:** Use `burnin_stats.positive_stats` and `negative_stats`
- **Make Textbox Optional:** Modify BurninStats to allow `textbox=None`
- **Format:** Label : value tables in PDF

---

## 📊 Metrics & Timeline

### Effort Estimation
- **Original Estimate:** 3 days
- **Breakdown:**
  - Day 1: Core architecture (model, factory, plotting, dialog) - 6 hours
  - Day 1-2: PDF generation (stats table, plots) - 6 hours
  - Day 2-3: Integration & wiring - 4 hours
  - Day 3: Testing & cleanup - 2 hours

### Key Milestones
- **Day 1 End:** Core architecture complete, factory wired
- **Day 2 End:** PDF generation complete with all content
- **Day 3 End:** Tested, cleaned, ready for merge

---

## File Manifest

### New Files to Create (4):
1. `src/testpad/ui/tabs/burnin_tab/__init__.py` - Factory function
2. `src/testpad/ui/tabs/burnin_tab/model.py` - BurninModel class
3. `src/testpad/ui/tabs/burnin_tab/plotting.py` - Pure matplotlib functions
4. `src/testpad/ui/tabs/burnin_tab/metadata_dialog.py` - Metadata input dialog

### Existing Files to Modify (5):
1. `src/testpad/ui/tabs/burnin_tab.py` - Fix signal, add model support
2. `src/testpad/ui/tabs/burnin_tab/burnin_presenter.py` - Full implementation
3. `src/testpad/ui/tabs/burnin_tab/generate_pdf_report.py` - Complete stats/graphs
4. `src/testpad/core/burnin/burnin_stats.py` - Make textbox optional
5. `src/testpad/ui/tabs/registry.py` - Use factory function

### Already Complete (2):
1. `src/testpad/ui/tabs/burnin_tab/report_layout.py` ✅
2. `src/testpad/core/burnin/burnin_graph.py` ✅ (reference only)

---

_Template Version: 1.0_
_Last Updated: 2025-10-28_
