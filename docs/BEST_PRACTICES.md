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