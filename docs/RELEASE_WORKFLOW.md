# Release Workflow Guide

This document outlines the production-level release workflow for Testpad, following industry best practices.

## Table of Contents

- [Overview](#overview)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Quick Start](#quick-start)
- [Detailed Workflow](#detailed-workflow)
- [Hotfix Workflow](#hotfix-workflow)
- [Additional Resources](#additional-resources)

## Overview

The release process follows these principles:

1. **Gitflow Branching Strategy**: Development happens on feature branches created from `dev`, releases are merged to `main`
2. **Semantic Versioning (SemVer)**: We use `MAJOR.MINOR.PATCH` versioning
3. **Automated Builds**: GitHub Actions handles compilation and packaging
4. **Draft Releases**: All releases start as drafts for review before publication
5. **Tag-Triggered**: Pushing a version tag automatically triggers the draft-release workflow
6. **Single Source of Truth**: Version is managed in `VERSION` file

## GitHub Actions Workflows

The release process is supported by several automated GitHub Actions workflows. Understanding when they trigger and what they do is key to the release process.

### feature-checks.yml

**Triggers:** When a PR is opened from a `feat/*`, `*refactor/*`, `*fix/*` or `*docs/*` branch into `dev`

**What it does:**
- Validates the branch name
- Checks out the code for the PR
- Runs linting and formatting with ruff
- Runs unit tests with coverage checks (`pytest`)
- Calculates code coverage
- Generates a PR comment that reports the results

### release-prep.yml

**Triggers:** When a PR is created from `release/*` or `hotfix/*` branch to `main`


**What it does:**
- Validates VERSION file format
- Checks semantic versioning compliance
- Runs full test suite
- Builds artifacts (for validation)
- Posts validation results as PR comment

**Artifacts:**
The build artifacts from this workflow are for **validation purposes** to ensure the code can be built successfully before merging to main. They are available in the GitHub Actions artifacts section of the workflow run.

- **Location**: Actions > release-prep workflow run > Artifacts
- **Purpose**: Verify the code builds without errors
- **Testing**: Optional - you can download and smoke test these, or wait to test the draft release artifacts
- **Retention**: 30 days

**Manual step required:**
- Review the validation results and manually merge the PR.
- Manually checkout main, tag and then push the tag to origin immediately after the merge
```bash
git checkout main
git pull --ff-only origin main         # Fetch merge commit, fail if diverge
git tag -a vx.y.z -m "Release vx.y.z"
git push origin vx.y.z                 # Push only the tag
```

### draft-release.yml

**Triggers:** When a tag (e.g., `v1.11.1`) is pushed

**What it does:**
- Checks out code at the tag
- Reads VERSION file
- Builds Windows artifacts (release bundle, portable executable, and Inno Setup file)
- Generates changelog from git commits
- Creates a **draft release** on GitHub with artifacts attached

**Artifacts:**
These are the **official release artifacts** that will be published and distributed to users.

- **Location**: Releases > Draft releases
- **Purpose**: Official release distribution
- **Testing**: **Required** - you must fully test these before publishing
- **Retention**: Permanent (attached to release)

**Manual step required:** 
- After this workflow completes, you must test the draft release artifacts before proceeding.
- Manually publish the draft as a public release after validating the artifacts

### hotfix-checks.yml (optional variant)

**Triggers:** When a PR is created from `hotfix/*` branch to `main`

**What it does:**
- Similar to release-prep.yml but optimized for hotfixes
- Validates patch version bump only
- Runs critical tests (faster subset)
- Security scans

**Manual step required:** 
- Review and manually merge the PR.
- Follow same manual tagging procedure as in [release-prep.yml](#release-prep.yml)

**Note:** For complete details on all workflows, see [WORKFLOWS_SUMMARY.md](WORKFLOWS_SUMMARY.md).

## Quick Start
  Feature Development

  1. Create feature branch from dev (`git checkout -b feat/my-feature`)
  2. Develop and commit changes
  3. Push feature branch (git push origin feat/my-feature)
  4. Create PR: feat/my-feature → dev → triggers feature-checks.yml (runs tests)
  5. Review and merge PR to dev
  6. Delete feature branch

  Release Process

  7.  Create release branch from dev (`git checkout -b release/v1.11.1`)
  8.  Bump version (`python scripts/bump_version.py patch`)
  9.  Create PR `release/v1.11.1` → `main` → triggers `release-prep.yml` 
  10. Manually review and merge PR
  11. Manually tag the merge commit → triggers `publish-release.yml`
      ```bash
      git checkout main
      git pull --ff-only origin main
      git tag -a vx.y.z -m "Release vx.y.z"
      git push origin vx.y.z
      ```
  12. Manually test draft release artifacts
      - download artifacts
      - Verify functionality  
  13. Manually create PR `main` → `dev`
  14. Manually merge PR `main` → `dev`
  15. Manually publish the draft release (GitHub UI)

Commands for creating `release/*` branch
```bash
# 1. Create a release branch from dev
git checkout dev
git pull origin dev
git checkout -b release/v1.11.1

# 2. After all work on release/* is complete,
# run version bump script on release branch (creates local commit)
python scripts/bump_version.py patch

# 3. Create PR to trigger release-prep workflow
git log -1 --stat
gh pr create      # Interactive mode - use flags, github desktop, or github web
# ⚙️ This triggers: release-prep.yml 

# 4. Monitor the GitHub Actions workflow
# Visit: https://github.com/fusinstruments/summer_2024/testpad/actions
# Wait for release-prep.yml to complete

# 5. Test the artifact builds from the workflow
# Download artifacts from the workflow and test

# 6. Create PR: release branch → main
gh pr create --base main --head release/v1.11.1 \
  --title "Release v1.11.1" --body "Release v1.11.1"
# ⚙️ This triggers: release-prep.yml (validates PR)

# 7. Review and merge PR to main
# Manually review and merge via GitHub UI

# 8. Manually tag the merge commit and push the tag
git checkout main
git pull --ff-only origin main
git tag -a vx.y.z -m "Release vx.y.z"
git push origin vx.y.z
# the push command will trigger draft-release.yml workflow

# 9. Validate the draft release artifacts and review release notes

# 10. Create PR: main → dev
gh pr create --base dev --head main \
  --title "Merge main to dev" --body "Sync main to dev"

# 11. Review and merge PR to dev
# Manually review and merge via GitHub UI

# 12. Delete release branch
git branch -d release/v1.11.1
git push origin --delete release/v1.11.1

# 13. Publish the draft release
# Visit: https://github.com/fusinstruments/summer_2024/releases
# Click "Edit" on draft → Click "Publish release"
```

## Detailed Workflow

### 1. Pre-Release Checklist

Before creating a release, ensure:

- [ ] All feature/fix branches are merged to `dev`
- [ ] All tests pass locally and in CI on `dev`
- [ ] Documentation is updated
- [ ] Working directory is clean (`git status` shows no changes)
- [ ] Local `dev` branch is up-to-date with remote

```bash
# Verify everything is ready
git checkout dev
git pull origin dev
git status  # Should show "nothing to commit, working tree clean"

# Create release branch
git checkout -b release/v1.11.1  # or whatever version you're releasing
```

**Branching Strategy (Gitflow):**
- `main` - Production branch (stable releases only)
- `dev` - Development branch (integration branch for features)
- `release/*` - Release preparation branches (created from dev, merged to both main and dev)
- `feature/*` - Feature branches (created from and merged to dev)
- `hotfix/*` - Hotfix branches (created from main, merged to both main and dev)
- `refactor/*` - Branch where only refactors were done - functionality not changed
- `docs/*` - Docs or CI/CD updated but no other code changes

**Workflow:**
- **Feature development**: feature/* → dev
- **Release**: dev → release/* → (build & test) → main → dev → publish release
- **Hotfix**: main → hotfix/* → (fix & test) → main → dev
- **Refactor**: refactor/* → dev
- **Docs**: docs/* → dev

### 2. Version Bumping

Once on the release branch, use the `bump_version.py` script to increment the version following [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes (`2.0.0 → 3.0.0`)
- **MINOR** version: New features, backward compatible (`2.1.0 → 2.2.0`)
- **PATCH** version: Bug fixes, backward compatible (`2.1.0 → 2.1.1`)

```bash
# Ensure you're on the release branch
git checkout release/v1.11.1

# Preview changes (dry run)
python scripts/bump_version.py patch --dry-run

# Bump patch version (most common)
python scripts/bump_version.py patch

# Bump minor version (new features)
python scripts/bump_version.py minor

# Bump major version (breaking changes)
python scripts/bump_version.py major
```

The script will:
1. ✓ Check git status (clean working directory)
2. ✓ Verify you're on a `release/*`, `refactore/*` or `hotfix/*` branch (warns if not)
3. ✓ Check that tag doesn't already exist
4. ✓ Update VERSION file
5. ✓ Create git commit with message: `build: Bump version to X.Y.Z`

**The script does NOT automatically push.** This allows you to review changes before triggering the CI/CD pipeline.

**Interactive mode:** If you run the script without arguments, it will prompt you for the bump type and dry-run option:
```bash
python scripts/bump_version.py
# Prompts for: patch/minor/major and dry-run option
```

### 3. Review Create Pull Request

Review the changes and push when ready:

```bash
# Review the version bump commit
git log -1 --stat
git show HEAD

# Push the commit and the manually open a PR
git push origin release/v1.11.1
```

Manually create a Pull Request from `release/*` into `main`

**⚙️ GitHub Actions Trigger:** This PR triggers the `release-prep.yml` workflow, which:
- Checks out code at the PR
- Runs linting, type-checking, formatting checks
- Builds Windows release artifacts (release bundle, portable executable and setup file)
- Adds a summary as a PR comment to the opened PR

### 4. Manually Approve PR

Once you have verified the artifacts function correctly, manually approve the PR, followed by creating the tag and pushing it.
```bash
git checkout main
git pull --ff-only origin main
git tag -a vx.y.z -m "Release vx.y.z"
git push origin vx.y.z
```
This will trigger the next step.

### 5. Automated Build Process (publish-release.yml)

Once the tag is pushed, the `draft-release.yml` GitHub Actions workflow automatically:

1. **Checks out code** at the tag commit
2. **Reads VERSION file** to get version number
3. **Builds Windows Release** (one-directory bundle)
4. **Builds Windows Portable** (single executable)
5. **Builds Windows installer** (inno setup file of one-dir build)
6. **Generates Changelog** (from git commits since last tag)
7. **Creates Draft Release** on GitHub with:
   - Release title: "Release v{VERSION}"
   - Auto-generated changelog in release notes
   - Both build artifacts attached (`.zip` files)
   - **Status: DRAFT** (not published yet)

**Monitor the workflow:** Visit `https://github.com/fusinstruments/summer_2024/testpad/actions` to watch the build progress.

**What happens next:** Once the workflow completes successfully, a draft release will be available at `https://github.com/fusinstruments/summer_2024/releases`. You should test the artifacts before proceeding.

### 6. Test the Draft Release

Before creating PRs to merge `main` into `dev` and publishing the draft release:

1. **Navigate to Releases**: Go to `https://github.com/fusinstruments/summer_2024/releases`
2. **Find the draft release** for your version (e.g., "Release v1.11.1")
3. **Download both artifacts**:
   - `testpad-v1.11.1-windows-release.zip`
   - `testpad-v1.11.1-windows-portable.zip`
4. **Test the builds**:
   - Extract and run the release bundle
   - Test the portable executable
   - Run the setup file and test the installed version
   - Verify functionality works as expected
5. **Document any issues** - If there are problems, you may need to roll back

### 7. Create Pull Requests (main into dev)

Once you've verified the draft release artifacts work correctly, create a PR to merge main into dev :

**Create PR to main:**
```bash
gh pr create --base dev --head main \
  --title "Release v1.11.1" \
  --body "Release v1.11.1 - merging to dev"
```

### 8. Merge Pull Requests

Once you have reviewed the PR, manually accept the merge:

1. **Review the PRs** on GitHub
2. **Manually approve and merge PR to dev** (via GitHub UI)

### 9. Publish the Draft Release

After `main` has been merged into `dev`:

1. **Navigate to Releases**: Go to `https://github.com/fusinstruments/summer_2024/releases`

2. **Find the draft release** for your version

3. **Edit the release notes** (optional):
   - Add highlights or important notes at the top
   - Group related changes by type (Features, Bug Fixes, etc.)
   - Add breaking changes section if applicable
   - Edit commit messages to be more user-friendly

4. **Publish the Release**:
   - Click "Edit" on the draft release
   - Review everything one final time
   - Click "Publish release" button
   - This makes it public and notifies watchers

### 10. Clean Up

After publishing the release:

```bash
# Delete local release branch
git branch -d release/v1.11.1

# Delete remote release branch
git push origin --delete release/v1.11.1
```

### 11. Post-Release Checklist

- [ ] Version bumped and tag created on release branch
- [ ] PR created to main and validated by `release-prep.yml`
- [ ] Artifacts tested
- [ ] PR Manually merged into `main`
- [ ] Manually tag merge commit on `main`
- [ ] Push tag, triggering `draft-release.yml`
- [ ] Draft release published on GitHub
- [ ] Release appears correctly and is downloadable
- [ ] PR opened to merge `main` back into `dev`
- [ ] Release branch deleted
- [ ] Team/users notified of the new release
- [ ] External documentation updated if needed

## Hotfix Workflow

When a critical bug is found in production (on `main`), use the hotfix workflow:

### 1. Create Hotfix Branch

```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/v1.11.2
```

### 2. Fix the Issue

Make the necessary fixes on the hotfix branch, ensuring:

- [ ] The fix addresses the critical issue
- [ ] Tests are added/updated to prevent regression
- [ ] Code is tested locally

### 3. Version Bump

```bash
# Bump version (typically a patch)
python scripts/bump_version.py patch

# Review and push
git log -1 --stat
git push origin hotfix/v1.11.2
```

### 4. Open PR manually

Open a PR through one of the following:
- GitHub Desktop UI
- GitHub web UI
- GitHub CLI (`gh pr create`)

This triggers the `release-prep.yml` workflow

### 5. Manually Approve PR

1. Wait for the `release-prep.yml` workflow to complete
2. Visit `https://github.com/fusinstruments/summer_2024/releases`
3. Download and test the hotfix artifacts
4. Approve the PR from `hotfix/*` into `main`

### 6. Manually tag and Push on main

**Manually tag and Push:**
```bash
git checkout main
git pull --ff-only origin main
git tag -a vx.y.z -m "Release vx.y.z"
git push origin vx.y.z
```

**⚙️ GitHub Actions Trigger:** This triggers `hotfix-checks.yml` (or `release-draft.yml`), which validates the hotfix.

**Create PR to dev:**
```bash
gh pr create --base dev --head main \
  --title "Merge hotfix v1.11.2 to dev" \
  --body "Sync hotfix to dev branch"
```

### 7. Merge Pull Requests

1. Review PR on GitHub
2. Manually approve and merge PR to dev

### 8. Publish Release and Clean Up

```bash
# Delete hotfix branch
git branch -d hotfix/v1.11.2
git push origin --delete hotfix/v1.11.2
```

Then:
- Navigate to GitHub Releases
- Edit the draft release if needed
- Publish the release
- Notify users of the critical fix

## Additional Resources

### Best Practices

For commit message guidelines, version bump timing, release notes enhancement, security considerations, and branch protection settings, see [BEST_PRACTICES.md](BEST_PRACTICES.md).

### Troubleshooting

For solutions to common problems including version bump script issues, GitHub Actions problems, tag creation errors, and rollback procedures, see  [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Workflow Reference
For a comprehensive summary of all GitHub Actions workflows and their triggers, see [WORKFLOWS_SUMMARY.md](WORKFLOWS_SUMMARY.md).
