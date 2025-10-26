# GitHub Actions Workflows Overview

## 1. **feature-checks.yml**

### Triggers
```yaml
on:
  pull_request:
    branches:
      - dev
    types: [opened, synchronize, reopened]
```
**When:** PR opened/updated from any `feat/*` branch → `dev`

### Actions
1. Checkout code
2. Set up language environment (Python, Node, etc.)
3. Install dependencies
4. Run linters/code formatters
5. Run unit tests
6. Run integration tests (if applicable)
7. Check code coverage
8. Post results as PR comment (pass/fail)

### Chains Into
❌ **No chaining** - This is a validation-only workflow. Human must manually merge PR after approval.

---

## 2. **dev-merge.yml** (Optional but recommended)

### Triggers
```yaml
on:
  push:
    branches:
      - dev
```
**When:** Any code is merged into `dev` branch

### Actions
1. Checkout code
2. Run full test suite
3. Build artifacts (optional)
4. Deploy to dev/staging environment (optional)
5. Send notification (Slack/email)

### Chains Into
❌ **No chaining** - Just validates dev branch stays healthy

---

## 3. **release-prep.yml**

### Triggers
```yaml
on:
  pull_request:
    branches:
      - main
      - dev
    types: [opened, synchronize]
  # Only for release and hotfix branches
  # Filter in workflow: if: startsWith(github.head_ref, 'release/') || startsWith(github.head_ref, 'hotfix/')
```
**When:** PR opened from `release/*` or `hotfix/*` → `main` OR `dev`

### Actions
1. Checkout code
2. **Validate VERSION file exists and is updated**
3. **Extract version from VERSION file**
4. **Check version follows semver format** (e.g., 1.2.3)
5. **Verify version is higher than current base branch version** (when targeting main)
6. Run full test suite
7. Run security scans (optional)
8. Build artifacts
9. **Check that tag exists for this version** (when targeting main - tag should be pushed before PR)
10. Post validation summary as PR comment

### Chains Into
❌ **No chaining** - Requires manual PR approval and merge

---

## 4. **publish-release.yml**

### Triggers
```yaml
on:
  push:
    tags:
      - 'v*'  # Triggered by tags like v1.2.0
```
**When:** Git tag pushed from `release/*` or `hotfix/*` branch

### Actions
1. Checkout code at tag
2. **Read VERSION file to get version number**
3. **Generate changelog** (from git commits since last tag)
4. Build production artifacts
   - Compile code (Windows release bundle)
   - Bundle assets (Windows portable executable)
   - Create distribution packages (.zip files)
5. Run final smoke tests on built artifacts (optional)
6. **Create GitHub Draft Release**
   - Title: "Release v{VERSION}"
   - Body: Auto-generated changelog
   - Attach built artifacts as release assets
   - **Status: DRAFT** (not published)

**Note:** This workflow creates a **draft release** for testing. The release is manually published after:
- Testing the draft release artifacts
- Merging release branch to both `main` and `dev` via PRs
- Final review and approval

### Chains Into
❌ **No automatic chaining** - Draft release must be manually published after PR merges complete

---

## 5. **hotfix-checks.yml**

### Triggers
```yaml
on:
  pull_request:
    branches:
      - main
    types: [opened, synchronize]
  # Only for hotfix branches
  # Filter: if: startsWith(github.head_ref, 'hotfix/')
```
**When:** PR opened from `hotfix/*` → `main`

### Actions
1. Checkout code
2. **Validate VERSION file bumped (patch only)**
3. Run critical tests only (faster than full suite)
4. Security scan
5. **Verify it's a patch version bump** (1.2.3 → 1.2.4, not 1.3.0)
6. Post results

### Chains Into
❌ **No chaining** - After manual merge, triggers **publish-release.yml** (via tag push)


---

## Summary Table

| Workflow | Trigger | Manual Gate? | Chains To |
|----------|---------|--------------|-----------|
| feature-checks.yml | PR to `dev` | ✅ Yes (merge PR) | ❌ None |
| dev-merge.yml | Push to `dev` | ❌ No | ❌ None |
| release-prep.yml | PR from release/* to `main`/`dev` | ✅ Yes (merge PR) | ❌ None |
| publish-release.yml | Tag push (v*) from release/hotfix branch | ✅ Yes (publish draft) | ❌ None |
| hotfix-checks.yml | PR from hotfix/* to main | ✅ Yes (merge PR) | ❌ None |

---

**Key Points:**
- **Manual gates** prevent accidental releases
- **Tag push creates a DRAFT release** for testing (not published automatically)
- **Validation happens in PR workflows** (release-prep.yml, hotfix-checks.yml)
- **Draft release is manually published** after all PRs are merged
- **Full control**: Every step requires human approval (merge PRs, publish release)