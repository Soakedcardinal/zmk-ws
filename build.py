import subprocess
import re
import sys
from pathlib import Path

# Set path to zmk-config relative to the script location
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR / "zmk-config"

def run_git_command(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error running {' '.join(cmd)}:\n{result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()

def get_latest_tag(repo_dir):
    run_git_command(["git", "fetch", "--tags"], cwd=repo_dir)
    tags = run_git_command(["git", "tag"], cwd=repo_dir).splitlines()
    
    # Filter only tags that match semantic versioning like v1.2.3 or 1.2.3
    version_tags = [t for t in tags if re.match(r'^v?\d+\.\d+(\.\d+)?$', t)]
    
    if not version_tags:
        print("❌ No valid semantic version tags found.")
        sys.exit(1)
    
    # Sort tags by version
    def version_key(tag):
        return list(map(int, re.sub('^v', '', tag).split('.')))

    latest = sorted(version_tags, key=version_key)[-1]
    return latest


def bump_minor(tag):
    match = re.match(r"v?(\d+)\.(\d+)", tag)
    if not match:
        print(f"❌ Unsupported tag format: {tag}")
        sys.exit(1)
    major, minor = map(int, match.groups())
    return f"v{major}.{minor + 1}.0"

def create_and_push_tag(tag, repo_dir):
    run_git_command(["git", "tag", tag], cwd=repo_dir)
    run_git_command(["git", "push", "origin", tag], cwd=repo_dir)
    print(f"✅ Created and pushed tag: {tag}")

def main():
    if not REPO_DIR.exists():
        print(f"❌ Directory not found: {REPO_DIR}")
        sys.exit(1)

    print(f"📁 Working in: {REPO_DIR}")
    latest_tag = get_latest_tag(REPO_DIR)
    print(f"🔖 Latest tag: {latest_tag}")
    new_tag = bump_minor(latest_tag)
    print(f"⏫ Bumping to: {new_tag}")
    create_and_push_tag(new_tag, REPO_DIR)

if __name__ == "__main__":
    main()
