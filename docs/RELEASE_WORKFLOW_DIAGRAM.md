# Release Workflow Diagram

Visual representation of the Testpad release process following Gitflow strategy.

## Branch Strategy

```
main (production)
  │
  ├─── dev (development)
  │      │
  │      ├─── feature/* (feature branches)
  │      └─── fix/* (bug fix branches)
  │
  ├─── release/* (release preparation)
  └─── hotfix/* (production fixes)
```

## Complete Release Flow
**Note:** All \<workflow>.yml files refers to a GitHub Actions workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. FEATURE DEVELOPMENT                       │
└─────────────────────────────────────────────────────────────────┘

dev ──> Create feature/new-feature ──> Make changes ──> Push branch
                                                              │
                                                              ▼
            ┌───────────────────────────────────────────────────┐
            │ Create PR: feature/new-feature → dev              │
            │                                                   │
            │   Triggers: feature-checks.yml                    │
            │   - Run linters/formatters                        │
            │   - Run unit tests                                │
            │   - Run integration tests                         │
            │   - Check code coverage                           │
            │   - Post results as PR comment                    │
            └───────────────────────────────────────────────────┘
                                  │
                         [Manual Review & Merge]
                                  │
                                  ▼
                                dev (updated)
                                  │
                                  ▼
                         develop-merge.yml (optional)
                         - Run full test suite
                         - Send notification


┌─────────────────────────────────────────────────────────────────┐
│                    2. RELEASE PREPARATION                       │
└─────────────────────────────────────────────────────────────────┘

dev ──> Create release/v1.11.1 ──> bump_version.py ──> Create tag v1.11.1


┌─────────────────────────────────────────────────────────────────┐
│                    3. BUILD & TEST                              │
└─────────────────────────────────────────────────────────────────┘

Push tag ──> publish-release.yml ──> Draft Release ──> Test artifacts
                                       - release.zip
                                       - portable.exe
                                       - setup.exe
                                       - Changelog


┌─────────────────────────────────────────────────────────────────┐
│                    4. VALIDATION & MERGE                        │
└─────────────────────────────────────────────────────────────────┘

                    ┌──> [PR to main] ──> release-prep.yml ──> [Merge]
release/v1.11.1 ──┤
                    └──> [PR to dev] ──> release-prep.yml ──> [Merge]


┌─────────────────────────────────────────────────────────────────┐
│                    5. PUBLICATION                               │
└─────────────────────────────────────────────────────────────────┘

Publish draft release ──> Public release ──> Users download
```

## Detailed Step-by-Step Flow

```
Developer Actions              GitHub Actions              Result
─────────────────             ──────────────             ──────

1. Create release branch
   release/v1.11.1
        │
        ▼
2. Run version_bump.py
   - Updates VERSION
   - Updates pyproject.toml
   - Creates local tag
        │
        ▼
3. Push branch + tag    ──────> publish-release.yml
                                - Checkout at tag
                                - Build artifacts      ──> Draft Release
                                - Generate changelog       v1.11.1
                                - Create draft
        │
        ▼
4. Test draft artifacts
   - Download & verify
   - Test functionality
        │
        ▼
5. Create PRs          ──────> release-prep.yml
   - PR to main                - Validate VERSION
   - PR to dev                 - Run tests           ──> PR checks pass
                                - Verify tag
        │
        ▼
6. Merge PRs (manual)
   - Merge to main
   - Merge to dev
        │
        ▼
7. Publish release
   - Edit release notes
   - Click "Publish"    ──────────────────────────> Public Release
        │
        ▼
8. Clean up
   - Delete release branch
```

## Feature Development Flow (Detailed)

```
Developer Actions              GitHub Actions              Result
─────────────────             ──────────────             ──────

1. Create feature branch
   from dev
        │
        ▼
2. Make changes
   Commit code
        │
        ▼
3. Push branch to remote
        │
        ▼
4. Create PR to dev    ──────> feature-checks.yml
                                - Setup environment
                                - Install dependencies
                                - Run linters         ──> PR checks
                                - Run unit tests          (pass/fail)
                                - Check coverage
                                - Post comment
        │
        ▼
5. Address feedback
   Update PR if needed ──────> feature-checks.yml
                                (runs again)
        │
        ▼
6. Manual review & merge
        │
        ▼
7. Feature merged      ──────> develop-merge.yml
   to dev                      - Run full tests      ──> Notification
                                - Optional deploy         sent
```

## Hotfix Flow

```
main ──> hotfix/v1.11.2 ──> Version bump ──> Push tag
              │
              │──> publish-release.yml ──> Draft Release
              │
              │──> Test artifacts
              │
              ├──> [PR to main] ──> hotfix-checks.yml ──> Merge
              │
              └──> [PR to dev] ──> release-prep.yml ──> Merge

Publish release ──> Production fix deployed
```

## State Transitions

```
                         ┌──────────────┐
                         │ Development  │
                         │   on dev     │
                         └──────┬───────┘
                                │
                         All features ready
                                │
                                ▼
                         ┌──────────────┐
                         │Create release│
                         │    branch    │
                         └──────┬───────┘
                                │
                        Version bump + tag
                                │
                                ▼
                         ┌──────────────┐
                         │   Build &    │──> Artifacts
                         │   Draft      │
                         └──────┬───────┘
                                │
                          Test artifacts
                                │
                                ▼
                         ┌──────────────┐
                         │  Create PRs  │
                         │ main + dev   │
                         └──────┬───────┘
                                │
                      Review & merge PRs
                                │
                                ▼
                         ┌──────────────┐
                         │   Publish    │
                         │   Release    │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │    Users     │
                         │   Download   │
                         └──────────────┘
```

## Version Bump Decision Tree

```
                    Need to release?
                          │
                          ▼
              ┌───────────┴───────────┐
              │                       │
        Breaking change?          New feature?
              │                       │
              YES                     YES
              │                       │
              ▼                       ▼
        MAJOR bump              MINOR bump
        1.0.0 -> 2.0.0         1.11.0 -> 1.12.0
              │                       │
              └───────────┬───────────┘
                          │
                     Just fixes?
                          │
                          YES
                          │
                          ▼
                    PATCH bump
                   1.11.0 -> 1.11.1
```

## GitHub Actions Triggers

```
Event                    Workflow              Action
─────                   ────────              ──────

PR to dev               feature-checks.yml    Run tests & lint
from feature/*

Push to dev             develop-merge.yml     Run full tests
(after merge)                                 Send notification

PR to main/dev          release-prep.yml      Validate VERSION
from release/*                                Run tests
                                              Verify tag

Tag push                publish-release.yml   Build artifacts
(v1.11.1)                                     Create draft release

PR to main              hotfix-checks.yml     Validate patch version
from hotfix/*                                 Run critical tests
```

## Branching Timeline

```
Time ────────────────────────────────────────────────────>

feature/new-feature
    ├────> PR merged
    │           ▼
                dev ──────●────────●────────●───>
                          │        │
                    release/v1.11.1│
                          │        │
                          ├─> main ●
                          │  (v1.11.1)
                          │
                          └─> dev
                              (merged back)
```

## Safety Mechanisms

```
┌──────────────────────────────────────────────────────┐
│ Checkpoint         │ What's Verified                 │
├────────────────────┼─────────────────────────────────┤
│ Version bump       │ Clean working directory         │
│                    │ Correct branch                  │
│                    │ Tag doesn't exist               │
├────────────────────┼─────────────────────────────────┤
│ Local review       │ Review before push              │
│                    │ Can rollback easily (git reset) │
├────────────────────┼─────────────────────────────────┤
│ Draft release      │ Build succeeds                  │
│                    │ Artifacts created               │
│                    │ Manual testing required         │
├────────────────────┼─────────────────────────────────┤
│ PR validation      │ Tests pass                      │
│ (release-prep.yml) │ VERSION correct                 │
│                    │ Tag exists                      │
├────────────────────┼─────────────────────────────────┤
│ Manual PR merge    │ Human approval required         │
│                    │ Both main & dev updated         │
├────────────────────┼─────────────────────────────────┤
│ Manual publish     │ Final review                    │
│                    │ Explicit action to go public    │
└────────────────────┴─────────────────────────────────┘
```

## Quick Reference

### Feature Development (7 steps)

1. Create feature branch from dev
2. Make changes and commit
3. Push branch to remote
4. Create PR to dev
5. Wait for checks (automated)
6. Address feedback if needed
7. Merge PR

**Time:** Varies (depends on feature complexity)
**Manual steps:** 5
**Automated:** Linting, testing, coverage checks

### Standard Release (11 steps)

1. Create release branch from dev
2. Run `version_bump.py`
3. Review changes locally
4. Push branch + tag
5. Wait for build (automated)
6. Test draft release
7. Create PR to main
8. Create PR to dev
9. Merge both PRs
10. Publish draft release
11. Delete release branch

**Time:** 20-40 minutes (mostly build + testing)
**Manual steps:** 9
**Automated:** Build & validation

### Rollback Scenarios

```
Before push:    git reset --hard HEAD~1 && git tag -d v1.x.x
After push:     Delete tag, revert commits, restart
Draft only:     Just don't publish (delete draft)
After publish:  Create hotfix with new version
```

## Common Patterns

### Multiple Features in One Release

```
dev ──> feature-1 merged
    ──> feature-2 merged  } All ready
    ──> fix-1 merged      }
         │
         └──> Create release/v1.12.0 ──> Version bump ──> Release
```

### Back-to-Back Releases

```
release/v1.11.1 ──> Published
                          │
                     (wait 1 hour+)
                          │
                          └──> release/v1.11.2 ──> Published
```

### Release with Breaking Changes

```
dev (v1.x) ──> Major changes ──> release/v2.0.0
                                       │
                                 version_bump.py major
                                       │
                                    v2.0.0 ──> Published
```

## File Changes During Release

```
release/v1.11.1 created
        │
        ├─ VERSION:       "1.11.0" -> "1.11.1"
        ├─ pyproject.toml: version = "1.11.1"
        └─ Git tag:       v1.11.1 created
```

## Summary

**Workflow Type:** Gitflow with release branches
**Automation Level:** High (builds, testing, validation)
**Manual Gates:** 6 (branch creation, push, test, PR review, merge, publish)
**Safety Checkpoints:** 6
**Average Release Time:** 20-40 minutes
**Rollback Difficulty:** Easy (before push) → Medium (after publish)

**Key Principle:** Test before merging to main, publish after merging.
