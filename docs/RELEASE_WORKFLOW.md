# Release Workflow Guide

This document outlines the production-level release workflow for Testpad, following industry best practices.

## Table of Contents

- [Overview](#overview)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Quick Start](#quick-start)
- [Detailed Workflow](#detailed-workflow)
- [Hotfix Workflow](#hotfix-workflow)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The release process follows these principles:

1. **Gitflow Branching Strategy**: Development happens on `dev`, releases are merged to `main`
2. **Semantic Versioning (SemVer)**: We use `MAJOR.MINOR.PATCH` versioning
3. **Automated Builds**: GitHub Actions handles compilation and packaging
4. **Draft Releases**: All releases start as drafts for review before publication
5. **Tag-Triggered**: Pushing a version tag automatically triggers the release workflow
6. **Single Source of Truth**: Version is managed in `VERSION` file

## GitHub Actions Workflows

The release process is supported by several automated GitHub Actions workflows. Understanding when they trigger and what they do is key to the release process.

### publish-release.yml

**Triggers:** When a tag (e.g., `v1.11.1`) is pushed from a `release/*` or `hotfix/*` branch

**What it does:**
- Checks out code at the tag
- Reads VERSION file
- Builds Windows artifacts (release bundle + portable executable)
- Generates changelog from git commits
- Creates a **draft release** on GitHub with artifacts attached

**Manual step required:** After this workflow completes, you must test the draft release artifacts before proceeding.

### release-prep.yml

**Triggers:** When a PR is created from `release/*` or `hotfix/*` branch to `main` or `dev`

**What it does:**
- Validates VERSION file format
- Checks semantic versioning compliance
- Verifies tag exists (when targeting main)
- Runs full test suite
- Builds artifacts
- Posts validation results as PR comment

**Manual step required:** Review the validation results and manually merge the PR.

### hotfix-checks.yml (optional variant)

**Triggers:** When a PR is created from `hotfix/*` branch to `main`

**What it does:**
- Similar to release-prep.yml but optimized for hotfixes
- Validates patch version bump only
- Runs critical tests (faster subset)
- Security scans

**Manual step required:** Review and manually merge the PR.

**Note:** For complete details on all workflows, see [WORKFLOWS_SUMMARY.md](WORKFLOWS_SUMMARY.md).

## Quick Start

```bash
# 1. Create a release branch from develop
git checkout dev
git pull origin dev
git checkout -b release/v1.11.1

# 2. Run version bump script on release branch (creates local commit + tag)
python scripts/version_bump.py patch

# 3. Review changes and push to trigger release workflow
git log -1 --stat
git push origin release/v1.11.1 --follow-tags
# ⚙️ This triggers: publish-release.yml (creates draft release)

# 4. Monitor the GitHub Actions workflow
# Visit: https://github.com/<your-org>/testpad/actions
# Wait for publish-release.yml to complete

# 5. Test the draft release build
# Download artifacts from draft release and test

# 6. Create PR: release branch → main
gh pr create --base main --head release/v1.11.1 \
  --title "Release v1.11.1" --body "Release v1.11.1"
# ⚙️ This triggers: release-prep.yml (validates PR)

# 7. Review and merge PR to main
# Manually review and merge via GitHub UI

# 8. Create PR: release branch → dev
gh pr create --base dev --head release/v1.11.1 \
  --title "Merge release v1.11.1 to dev" --body "Sync release to dev"
# ⚙️ This triggers: release-prep.yml (validates PR)

# 9. Review and merge PR to dev
# Manually review and merge via GitHub UI

# 10. Delete release branch
git branch -d release/v1.11.1
git push origin --delete release/v1.11.1

# 11. Publish the draft release
# Visit: https://github.com/<your-org>/testpad/releases
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

**Workflow:**
- **Feature development**: feature/* → dev
- **Release**: dev → release/* → (build & test) → main + dev → publish release
- **Hotfix**: main → hotfix/* → (fix & test) → main + dev

### 2. Version Bumping

Once on the release branch, use the `version_bump.py` script to increment the version following [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes (`2.0.0 → 3.0.0`)
- **MINOR** version: New features, backward compatible (`2.1.0 → 2.2.0`)
- **PATCH** version: Bug fixes, backward compatible (`2.1.0 → 2.1.1`)

```bash
# Ensure you're on the release branch
git checkout release/v1.11.1

# Preview changes (dry run)
python scripts/version_bump.py patch --dry-run

# Bump patch version (most common)
python scripts/version_bump.py patch

# Bump minor version (new features)
python scripts/version_bump.py minor

# Bump major version (breaking changes)
python scripts/version_bump.py major
```

The script will:
1. ✓ Check git status (clean working directory)
2. ✓ Verify you're on a `release/*` or `hotfix/*` branch (warns if not)
3. ✓ Check that tag doesn't already exist
4. ✓ Update VERSION file
5. ✓ Create git commit with message: `build: Bump version to X.Y.Z`
6. ✓ Create annotated git tag locally (e.g., `v1.11.1`)

**The script does NOT automatically push.** This allows you to review changes before triggering the CI/CD pipeline.

**Interactive mode:** If you run the script without arguments, it will prompt you for the bump type and dry-run option:
```bash
python scripts/bump_version.py
# Prompts for: patch/minor/major and dry-run option
```

**⚠️ IMPORTANT:** Run `bump_version.py` as the **LAST commit** on your release branch. If you make additional commits after bumping the version, the tag will point to the wrong commit. If you need to make changes after version bump, see "Rolling back before push" below.

### 3. Review and Push

Review the changes and push when ready:

```bash
# Review the version bump commit
git log -1 --stat
git show HEAD

# Verify the tag was created
git tag -l

# Push the commit and tag to trigger the release workflow
git push origin release/v1.11.1 --follow-tags
```

**⚙️ GitHub Actions Trigger:** This push triggers the `publish-release.yml` workflow, which:
- Detects the pushed tag (e.g., `v1.11.1`)
- Checks out code at that tag
- Builds Windows release artifacts (release bundle + portable executable)
- Generates changelog from git commits since last tag
- Creates a **draft release** on GitHub with artifacts attached

**Rolling back before push:** If you need to make changes before pushing, simply delete the tag and reset:
```bash
git tag -d v1.11.1           # Delete the tag
git reset --hard HEAD~1      # Remove the version bump commit
# Now you can make other changes, then re-run bump_version.py
```

**⚠️ If you find a bug AFTER running bump_version.py:**

The tag points to a specific commit. If you make additional commits, the tag won't include them in the build!

**Correct approach:**
```bash
# 1. Undo the version bump
git tag -d v1.11.1
git reset --hard HEAD~1

# 2. Fix the bug and commit
git add .
git commit -m "fix: critical bug description"

# 3. Re-run version bump (creates new tag at current HEAD)
python scripts/bump_version.py patch
```

### 4. Automated Build Process (publish-release.yml)

Once the tag is pushed, the `publish-release.yml` GitHub Actions workflow automatically:

1. **Checks out code** at the tag commit
2. **Reads VERSION file** to get version number
3. **Builds Windows Release** (one-directory bundle)
4. **Builds Windows Portable** (single executable)
5. **Generates Changelog** (from git commits since last tag)
6. **Creates Draft Release** on GitHub with:
   - Release title: "Release v{VERSION}"
   - Auto-generated changelog in release notes
   - Both build artifacts attached (`.zip` files)
   - **Status: DRAFT** (not published yet)

**Monitor the workflow:** Visit `https://github.com/<your-org>/testpad/actions` to watch the build progress.

**What happens next:** Once the workflow completes successfully, a draft release will be available at `https://github.com/<your-org>/testpad/releases`. You should test the artifacts before proceeding.

### 5. Test the Draft Release

Before creating PRs to merge the release:

1. **Navigate to Releases**: Go to `https://github.com/<your-org>/testpad/releases`
2. **Find the draft release** for your version (e.g., "Release v1.11.1")
3. **Download both artifacts**:
   - `testpad-v1.11.1-windows-release.zip`
   - `testpad-v1.11.1-windows-portable.zip`
4. **Test the builds**:
   - Extract and run the release bundle
   - Test the portable executable
   - Verify functionality works as expected
5. **Document any issues** - If there are problems, you may need to roll back

### 6. Create Pull Requests (release-prep.yml)

Once you've verified the draft release artifacts work correctly, create PRs to merge the release branch:

**Create PR to main:**
```bash
gh pr create --base main --head release/v1.11.1 \
  --title "Release v1.11.1" \
  --body "Release v1.11.1 - merging to main"
```

**⚙️ GitHub Actions Trigger:** This triggers the `release-prep.yml` workflow, which validates:
- VERSION file exists and is properly formatted
- Version follows semantic versioning
- Tag exists for this version
- All tests pass
- Builds complete successfully

**Create PR to dev:**
```bash
gh pr create --base dev --head release/v1.11.1 \
  --title "Merge release v1.11.1 to dev" \
  --body "Sync release changes back to dev branch"
```

**⚙️ GitHub Actions Trigger:** This also triggers `release-prep.yml` for validation.

**Review the PRs:** Check the workflow results and address any validation failures before proceeding.

### 7. Merge Pull Requests

Once both PRs pass validation:

1. **Review the PRs** on GitHub
2. **Manually approve and merge PR to main** (via GitHub UI)
3. **Manually approve and merge PR to dev** (via GitHub UI)

**Important:** Both PRs must be merged before publishing the release. This ensures the tag commit exists on both `main` and `dev` branches.

### 8. Publish the Draft Release

After both PRs are merged:

1. **Navigate to Releases**: Go to `https://github.com/<your-org>/testpad/releases`

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

### 9. Clean Up

After publishing the release:

```bash
# Delete local release branch
git branch -d release/v1.11.1

# Delete remote release branch
git push origin --delete release/v1.11.1
```

### 10. Post-Release Checklist

- [ ] Version bumped and tag created on release branch
- [ ] Tag pushed, triggering `publish-release.yml` workflow
- [ ] Draft release created with artifacts
- [ ] Draft release artifacts tested
- [ ] PR created to main and validated by `release-prep.yml`
- [ ] PR created to dev and validated by `release-prep.yml`
- [ ] Both PRs reviewed and merged
- [ ] Draft release published on GitHub
- [ ] Release appears correctly and is downloadable
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

### 3. Version Bump and Tag

```bash
# Bump version (typically a patch)
python scripts/version_bump.py patch

# Review and push to trigger build workflow
git log -1 --stat
git push origin hotfix/v1.11.2 --follow-tags
```

**⚙️ GitHub Actions Trigger:** This triggers `publish-release.yml`, creating a draft release with artifacts.

### 4. Monitor Build and Test

1. Wait for the `publish-release.yml` workflow to complete
2. Visit `https://github.com/<your-org>/testpad/releases`
3. Download and test the draft release artifacts

### 5. Create Pull Requests

**CRITICAL**: Hotfix branches must be merged to BOTH `main` AND `dev`

**Create PR to main:**
```bash
gh pr create --base main --head hotfix/v1.11.2 \
  --title "Hotfix v1.11.2" \
  --body "Critical hotfix for [describe issue]"
```

**⚙️ GitHub Actions Trigger:** This triggers `hotfix-checks.yml` (or `release-prep.yml`), which validates the hotfix.

**Create PR to dev:**
```bash
gh pr create --base dev --head hotfix/v1.11.2 \
  --title "Merge hotfix v1.11.2 to dev" \
  --body "Sync hotfix to dev branch"
```

**⚙️ GitHub Actions Trigger:** This triggers `release-prep.yml` for validation.

### 6. Merge Pull Requests

1. Review both PRs on GitHub
2. Manually approve and merge PR to main
3. Manually approve and merge PR to dev

### 7. Publish Release and Clean Up

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

## Best Practices

### Commit Message Guidelines

Since changelogs are auto-generated from commits, all commit messages **must** follow this strict format based on [Angular's Commit Message Guidelines](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md):

**Format:** `<type>:<short summary>`

Where `<type>` is one of the following:

| Type         | Description                                                                                         |
|--------------|-----------------------------------------------------------------------------------------------------|
| **build**    | Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm) |
| **ci**       | Changes to our CI configuration files and scripts (examples: Github Actions, SauceLabs)             |
| **docs**     | Documentation only changes                                                                          |
| **feat**     | A new feature                                                                                       |
| **fix**      | A bug fix                                                                                           |
| **perf**     | A code change that improves performance                                                             |
| **refactor** | A code change that neither fixes a bug nor adds a feature                                           |
| **test**     | Adding missing tests or correcting existing tests                                                   |

✅ **Good Examples:**
```
feat: Add dissolved oxygen measurement feature
fix: Resolve crash when loading corrupted data files
perf: Improve startup performance by 40%
docs: Update installation instructions
refactor: Simplify data processing logic
test: Add unit tests for oxygen sensor
build: Update PyInstaller to version 6.0
ci: Add automated release workflow
```

❌ **Bad Examples:**
```
fix stuff
wip
asdf
update
Add dissolved oxygen measurement
Fixed a bug
```

**Rules:**
- Type must be lowercase
- Use a colon `:` immediately after the type (no space before colon)
- Add a space after the colon before the summary
- Summary should be in imperative mood ("add feature" not "added feature")
- Summary should be concise (50 characters or less recommended)
- No period at the end of the summary

### Version Bump Timing

- **Frequent small releases** are better than infrequent large ones
- Release when a meaningful unit of work is complete
- Don't accumulate too many changes before releasing
- Consider releasing immediately after critical bug fixes

### Release Notes Enhancement

The auto-generated changelog is a starting point. Consider adding:

```markdown
## 🎉 Highlights

- **New Feature**: Dissolved oxygen measurement support
- **Performance**: 40% faster startup time
- **Bug Fix**: Resolved data corruption issue affecting 5% of users

## ⚠️ Breaking Changes

- Config file format updated (auto-migration included)

## 📝 What's Changed

[Auto-generated commit list]

## 🐛 Known Issues

- Issue #123: Minor UI glitch on high-DPI displays (workaround available)
```

### Security Considerations

- **Never commit secrets** to the repository
- Review `.gitignore` to exclude sensitive files
- The release workflow uses `GITHUB_TOKEN` (automatically provided, scoped to repo)
- Artifacts are publicly downloadable once released

### Branch Protection

Consider enabling GitHub branch protection on `main`:

- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Require conversation resolution before merging

## Troubleshooting

### Version Bump Script Issues

**Problem**: "Working directory has uncommitted changes"
```bash
# Solution: Commit or stash your changes
git status
git add .
git commit -m "Your commit message"
# Then retry version bump
```

**Problem**: Warning about being on wrong branch
```bash
# Script warns: "You're on branch 'dev'"
# Solution: Switch to a release or hotfix branch
git checkout -b release/v1.11.1

# Or if you really need to override (not recommended):
# Answer 'y' when prompted "Continue anyway?"
```

**Problem**: "Not in a git repository"
```bash
# Solution: Ensure you're in the project root
cd /path/to/testpad
python scripts/version_bump.py patch
```

**Problem**: "Tag already exists"
```bash
# Solution: Check existing tags
git tag -l
# Delete local tag if needed (careful!)
git tag -d v1.11.1
# Delete remote tag (only if workflow hasn't run!)
git push origin :refs/tags/v1.11.1
```

**Problem**: "I made commits after running bump_version.py and the build doesn't include my changes"

This happens because the tag points to the version bump commit, not your later commits.

```bash
# Solution: Rollback and re-run bump_version.py
git tag -d v1.11.1           # Delete tag
git reset --hard HEAD~1      # Undo version bump commit
# Your other commits are still there
python scripts/bump_version.py patch  # Re-create tag at current HEAD
```

**Prevention:** Always run `bump_version.py` as the LAST step on your release branch before pushing.

### GitHub Actions Issues

**Problem**: Workflow doesn't trigger

- Check that tag was pushed: `git ls-remote --tags origin`
- Verify workflow file syntax: `.github/workflows/release.yml`
- Check GitHub Actions tab for errors

**Problem**: Build fails

- Check the Actions log for specific error
- Verify `environment-release.yml` is up to date
- Ensure PyInstaller spec files are correct

**Problem**: Release artifacts are missing

- Check the "Package release artifacts" step in workflow logs
- Verify the zip file creation completed successfully
- Ensure artifact paths match in workflow file

### Manual Tag Creation (Not Recommended)

If you need to create a tag manually (e.g., if the bump_version.py script is not available):

```bash
# Update VERSION file manually
echo "1.11.1" > VERSION

# Commit changes
git add VERSION
git commit -m "build: Bump version to 1.11.1"

# Create annotated tag
git tag -a v1.11.1 -m "Release v1.11.1"

# Review before pushing
git log -1 --stat
git tag -l

# Push commit and tag to trigger workflow
git push origin release/v1.11.1 --follow-tags
```

### Rolling Back a Release

#### Before Pushing (Local Only)

If you haven't pushed yet, rollback is simple (see step 3 in the detailed workflow):

```bash
git tag -d v1.11.1           # Delete the tag
git reset --hard HEAD~1      # Remove the version bump commit
# Now you can re-run version_bump.py or make other changes
```

#### After Pushing (Remote Cleanup Required)

If you've already pushed and the workflow has run:

1. **Delete the release on GitHub**:
   - Go to GitHub Releases
   - Click "Edit" on the release
   - Delete the release (or mark as pre-release if you want to keep it)

2. **Delete the remote tag**:
   ```bash
   git tag -d v1.11.1                    # Delete local tag
   git push origin --delete v1.11.1      # Delete remote tag
   ```

3. **Revert the version bump commits** (if already merged to main/dev):
   ```bash
   # On each branch where it was merged
   git checkout main
   git revert <commit-hash-of-version-bump>
   git push origin main

   git checkout dev
   git revert <commit-hash-of-version-bump>
   git push origin dev
   ```

**Note**: After cleanup, you can start the release process again from the beginning.

## Next Steps

For suggested enhancements and future improvements to this workflow, see [WORKFLOW_IMPROVEMENTS.md](WORKFLOW_IMPROVEMENTS.md).

## Summary

This workflow provides:

- **Simplicity**: One command to create a release (`version_bump.py`)
- **Automation**: Building and packaging handled by CI/CD
- **Safety**: Draft releases for review before publication
- **Traceability**: Git tags linked to releases
- **Professional**: Follows industry standards (SemVer, semantic tagging, CI/CD)

For questions or improvements, please open an issue or discuss with the team.
