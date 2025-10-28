# Troubleshooting

## Version Bump Script Issues

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
python scripts/bump_version.py patch
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

## GitHub Actions Issues

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

## Manual Tag Creation (Not Recommended)

If you need to create a tag manually:

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

# Push commit and tag
git push origin release/v1.11.1 
```

## Rolling Back a Release

### Before Pushing (Local Only)

If you haven't pushed yet, rollback is simple (see step 3 in the detailed workflow):

```bash
git tag -d v1.11.1           # Delete the tag
git reset --hard HEAD~1      # Remove the version bump commit
# Now you can re-run bump_version.py or make other changes
```

### After Pushing (Remote Cleanup Required)

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

- **Simplicity**: One command to create a release (`bump_version.py`)
- **Automation**: Building and packaging handled by CI/CD
- **Safety**: Draft releases for review before publication
- **Traceability**: Git tags linked to releases
- **Professional**: Follows industry standards (SemVer, semantic tagging, CI/CD)

For questions or improvements, please open an issue or discuss with the team.
