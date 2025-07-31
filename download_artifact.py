import requests
import zipfile
import os
import shutil
import subprocess
from pathlib import Path

def load_env_file():
    """Load variables from .env file"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Error: .env file not found!")
        print("Create a .env file with:")
        print("GITHUB_TOKEN=your_token_here")
        print("GITHUB_OWNER=your_username")
        print("GITHUB_REPO=your_repo_name")
        return None
    return env_vars

def download_latest_artifact():
    # Load configuration from .env file
    env_vars = load_env_file()
    if not env_vars:
        return
    
    OWNER = env_vars.get("GITHUB_OWNER")
    REPO = env_vars.get("GITHUB_REPO")
    TOKEN = env_vars.get("GITHUB_TOKEN")
    
    if not all([OWNER, REPO, TOKEN]):
        print("Error: Missing required variables in .env file!")
        print("Required: GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO")
        return
    
    # Headers for authentication
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Get latest workflow run
        print("Getting latest workflow run...")
        runs_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"
        runs_response = requests.get(runs_url, headers=headers)
        runs_response.raise_for_status()
        
        runs = runs_response.json()["workflow_runs"]
        if not runs:
            print("No workflow runs found")
            return
            
        latest_run = runs[0]
        run_id = latest_run["id"]
        commit_sha = latest_run["head_sha"]
        print(f"Found run: {run_id} at commit {commit_sha}")
        
        # Get the latest tag for the commit
        tags_url = f"https://api.github.com/repos/{OWNER}/{REPO}/commits/{commit_sha}/tags"
        # Note: GitHub API does not have a direct endpoint to get tags for a commit,
        # so we'll get all tags and find the latest one pointing to the commit.
        # Instead, list tags and check which one points to this commit.
        
        tags_list_url = f"https://api.github.com/repos/{OWNER}/{REPO}/tags"
        tags_response = requests.get(tags_list_url, headers=headers)
        tags_response.raise_for_status()
        tags = tags_response.json()
        
        latest_tag = None
        for tag in tags:
            if tag["commit"]["sha"] == commit_sha:
                latest_tag = tag["name"]
                break
        
        if not latest_tag:
            # If no tag found pointing exactly to the commit, fallback to latest tag overall
            latest_tag = tags[0]["name"] if tags else "untagged"
        
        print(f"Using tag: {latest_tag}")
        
        # Get artifacts for this run
        artifacts_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/artifacts"
        artifacts_response = requests.get(artifacts_url, headers=headers)
        artifacts_response.raise_for_status()
        
        artifacts = artifacts_response.json()["artifacts"]
        if not artifacts:
            print("No artifacts found in latest run")
            return
            
        # Take the first artifact (or modify to choose specific one)
        artifact = artifacts[0]
        artifact_name = artifact["name"]
        download_url = artifact["archive_download_url"]
        
        print(f"Downloading artifact: {artifact_name}")
        
        # Download the artifact
        download_response = requests.get(download_url, headers=headers)
        download_response.raise_for_status()
        
        # Save to temp zip file
        zip_path = f"{artifact_name}.zip"
        with open(zip_path, "wb") as f:
            f.write(download_response.content)
        
        # Create timestamped directory under releases with tag prefix
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        releases_dir = Path("releases")
        releases_dir.mkdir(exist_ok=True)
        
        release_dir = releases_dir / f"{latest_tag}-{timestamp}"
        release_dir.mkdir()
        
        # Extract the zip
        print(f"Extracting to {release_dir}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(release_dir)
        
        # Clean up temp zip
        os.remove(zip_path)
        
        print(f"Success! Artifact extracted to ./{release_dir}/")
        print(f"Contents: {list(release_dir.iterdir())}")
        
        # Open new Explorer window (Windows only)
        if os.name == 'nt':
            subprocess.Popen(['explorer', str(release_dir.resolve())])
        else:
            print("Opening file explorer is only supported on Windows in this script.")
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_latest_artifact()
