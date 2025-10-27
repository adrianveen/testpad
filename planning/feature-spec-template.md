# New Feature: [Feature Name]

_Replace [Feature Name] with your feature title. This document defines WHAT the feature does._

---

## 1. Purpose

**Problem Statement:**
- What problem does this feature solve?
- Who are the users?
- What are the key use cases?

**Solution Overview:**
- Brief description of the solution
- Key capabilities enabled by this feature

---

## 2. User Flow

1. User [initiates the feature by...]
2. User [performs action...]
3. User [completes action...]
4. System [responds with...]

_(Add as many steps as needed to describe the complete user journey)_

---

## 3. Inputs

Document all data sources and how they flow into the system.

### Input Data Flow Table

| Source | Presenter hand-off | Model / State target | Notes |
| --- | --- | --- | --- |
| **User → [Field Name]** | `presenter.method_name(params)` | `model.method_name(params)` | Validation rules, data type, constraints |
| **Disk → [Import]** | `presenter.load_from_file(path)` | `model.load_data(path)` | File format, error handling |
| **[Other Source]** | `presenter.handle_input()` | `model.store_data()` | Additional notes |

### Input Validation Rules
- **[Field 1]:** Required/Optional, data type, range, format
- **[Field 2]:** Required/Optional, data type, range, format
- **[Field N]:** Required/Optional, data type, range, format

---

## 4. Outputs

Document all data outputs and how they're delivered to users.

### Output Data Flow Table

| Source | Presenter hand-off | Model / State target | Notes |
| --- | --- | --- | --- |
| **User → [Action]** | `presenter.trigger_output()` | `model.generate_output()` | Output format, delivery method |
| **Model → [Result]** | Returns `ResultType` | Dataclass/dict with output | Error handling approach |
| **User → [Export]** | `presenter.export_to_file(path)` | `model.export_data(path)` | File format specification |

### State Persistence Schema

Document the structure of persisted state:

- `schema_version`: Integer version for migration compatibility
- `[field_1]`: Description of data structure and purpose
- `[field_2]`: Description of data structure and purpose
- `[field_n]`: Description of data structure and purpose

---

## 5. Dependencies

### External Libraries
- **[Library Name]** - Purpose (e.g., PDF generation, plotting, etc.)
- **[Library Name]** - Purpose

### Internal Dependencies
- **[Module/Service]** - Why it's needed
- **[Module/Service]** - Why it's needed

### Optional Dependencies
- **[Library Name]** - Used for [optional feature], lazy-loaded

---

## 6. Performance Budget

Define measurable performance targets:

- **Initial Load Time:** ≤ [X] ms to render UI (no heavy imports on init)
- **Primary Operation:** ≤ [X] s for typical use case; ≤ [Y] s for edge cases
- **UI Responsiveness:** No single UI-thread task > [X] ms; background processing for long operations
- **Memory Usage:** Peak ≤ [X] MB during operation; steady-state ≤ [Y] MB above baseline
- **Output Size:** Typical output ≤ [X] MB; maximum ≤ [Y] MB

### How to Measure
- Log key metrics: `operation_name_ms`, `peak_mem_mb`
- Assert targets in tests or CI smoke tests
- Use profiling tools: [specify tools]

---

## 7. Non-Goals

Explicitly define what this feature will NOT do:

- ❌ No [excluded capability 1]
- ❌ No [excluded capability 2]
- ❌ No [excluded capability 3]

_(This prevents scope creep and clarifies boundaries)_

---

## 8. Acceptance Criteria

Define testable success criteria:

- [ ] Feature flag controls visibility correctly
- [ ] Required fields validated; actions disabled until valid input
- [ ] Long operations run in background with progress feedback
- [ ] Output matches specification; data integrity verified
- [ ] Error handling works; errors surfaced to user with actionable messages
- [ ] Performance budget met (see section 6)
- [ ] State persists correctly across sessions
- [ ] Heavy dependencies lazy-loaded (if applicable)

---

## 9. Rollout Plan

### Feature Flag
- **Flag Name:** `[feature_flag_name]`
- **Default State:** Off in `dev` and `prod`
- **Toggle Method:** Config file / CLI arg (`--enable-[feature]`)

### Testing Strategy
- Unit tests for core logic
- Integration tests with flag on/off
- QA sign-off before enabling by default
- CI runs with flag both enabled and disabled

### Rollout Steps
1. Merge to `dev` with flag OFF
2. Enable for internal testing (1 sprint)
3. Collect feedback, iterate
4. Enable by default in `dev`
5. Promote to `main` after validation

---

## 10. Open Questions / Risks

Document uncertainties and risks:

- **[Question 1]:** Description of open question
  - _Decision:_ [To be determined / Decided on X date]
- **[Risk 1]:** Description of potential risk
  - _Mitigation:_ How to address it
- **[Question N]:** Additional questions or concerns

---

## 11. Future Enhancements (Optional)

Features intentionally deferred for later:

- **[Enhancement 1]:** Description (why deferred, when to consider)
- **[Enhancement 2]:** Description
- **[Enhancement N]:** Description

---

_Template Version: 1.0_
_Last Updated: [Date]_
