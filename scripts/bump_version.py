#!/usr/bin/env python3
"""Version bumping script for semantic versioning.

Updates VERSION file, creates git commit and tag.

Usage:
    python scripts/bump_version.py major         # 1.2.3 -> 2.0.0
    python scripts/bump_version.py minor         # 1.2.3 -> 1.3.0
    python scripts/bump_version.py patch         # 1.2.3 -> 1.2.4
    python scripts/bump_version.py patch --dry-run
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> str:
    """Run shell command and return output."""
    result = subprocess.run(
        cmd, check=False, shell=True, capture_output=True, text=True
    )
    if check and result.returncode != 0:
        print(f"❌ ERROR: Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def check_git_status() -> None:
    """Ensure clean working directory."""
    status = run_command("git status --porcelain")
    if status:
        print("❌ ERROR: Working directory has uncommitted changes")
        print("   Please commit or stash your changes before bumping version")
        sys.exit(1)


def check_branch() -> None:
    """Warn if not on release/hotfix branch."""
    branch = run_command("git branch --show-current")
    if not (branch.startswith(("release/", "hotfix/", "refactor/"))):
        print(f"⚠️  WARNING: You're on branch '{branch}'")
        print("   Expected: release/* or hotfix/*")
        print("   Running version bump on the wrong branch can cause issues!")
        choice = input("\nContinue anyway? [y/N]: ").strip().lower()
        if choice not in ("y", "yes"):
            print("❌ Aborted")
            sys.exit(1)


def check_tag_exists(tag: str) -> bool:
    """Check if tag already exists."""
    result = subprocess.run(
        f"git tag -l {tag}", check=False, shell=True, capture_output=True, text=True
    )
    return bool(result.stdout.strip())


def read_version() -> str:
    """Read current version from VERSION file."""
    version_file = Path("VERSION")
    if not version_file.exists():
        print("❌ ERROR: VERSION file not found")
        sys.exit(1)
    return version_file.read_text().strip()


def parse_version(version_string: str) -> tuple[int, ...]:
    """Parse version string into major, minor, patch integers."""
    parts = version_string.split(".")
    if len(parts) != 3:
        print(f"❌ ERROR: Invalid version format '{version_string}'")
        print("   Expected format: major.minor.patch (e.g., 1.2.3)")
        sys.exit(1)

    try:
        return tuple(map(int, parts))
    except ValueError:
        print(f"❌ ERROR: Invalid version format '{version_string}'")
        print("   Version parts must be integers (e.g., 1.2.3, not 1.2.a)")
        sys.exit(1)


def bump_version(current_version: str, bump_type: str) -> str:
    """Calculate new version based on bump type."""
    major, minor, patch = parse_version(current_version)

    if bump_type == "major":
        major, minor, patch = major + 1, 0, 0
    elif bump_type == "minor":
        minor, patch = minor + 1, 0
    else:  # patch
        patch += 1

    return f"{major}.{minor}.{patch}"


def main() -> None:
    """Define and run main program logic."""
    # Read current version
    current = read_version()

    # Parse arguments or prompt interactively
    if len(sys.argv) >= 2:
        bump_type = sys.argv[1].lower()
        dry_run = "--dry-run" in sys.argv
    else:
        # Interactive mode
        print("Version Bump Tool")
        print("-" * 40)
        print(f"Current version: {current}\n")
        print("Select bump type:")
        print("  1. patch  (1.2.3 -> 1.2.4)")
        print("  2. minor  (1.2.3 -> 1.3.0)")
        print("  3. major  (1.2.3 -> 2.0.0)")

        choice = input("\nEnter choice [1-3]: ").strip()
        bump_map = {"1": "patch", "2": "minor", "3": "major"}
        bump_type = bump_map.get(choice)

        if not bump_type:
            print("❌ Invalid choice")
            sys.exit(1)

        dry_run_input = input("Dry run? [y/N]: ").strip().lower()
        dry_run = dry_run_input in ("y", "yes")

    # Validate bump type
    if bump_type not in ("major", "minor", "patch"):
        print(f"❌ ERROR: Invalid bump type '{bump_type}'")
        print("   Valid options: major, minor, patch")
        sys.exit(1)

    # Calculate new version
    new_version = bump_version(current, bump_type)
    tag = f"v{new_version}"

    # Dry run: show what would happen
    if dry_run:
        print("🔍 DRY RUN MODE")
        print(f"   Version: {current} -> {new_version}")
        print(f"   Tag: {tag}")
        print("\nNo changes made.")
        return

    # Pre-flight checks
    check_git_status()
    check_branch()

    if check_tag_exists(tag):
        print(f"❌ ERROR: Tag {tag} already exists")
        print(f"   Delete it first: git tag -d {tag}")
        sys.exit(1)

    # Update VERSION file
    Path("VERSION").write_text(new_version + "\n")

    # Create git commit
    run_command("git add VERSION")
    run_command(f'git commit -m "build: Bump version to {new_version}"')

    # Success
    print(f"✅ Version bumped: {current} -> {new_version}")
    print("   Updated: VERSION")
    print(f"   Created: commit + tag {tag}")
    print("\n📋 Next steps:")
    print("   1. Review: git log -1 --stat")
    print("   2. Push: git push origin <branch>")
    print("\n [CAUTION]  Rollback before push:")
    print("   git reset --hard HEAD~1")


if __name__ == "__main__":
    main()
