# zmk-ws

ZMK Keyboard Firmware Setup for Tightyl Keyboard

## Usage

First create an .env file with:

```.env
GITHUB_TOKEN=your_token
GITHUB_OWNER=your_username_or_org
GITHUB_REPO=your_repo_name
```

Then use python scripts:

```powershell
python .\build.py

python .\download_artifact.py
```

or in vscode/vscodium, CTL+SHIFT+B to build using github actions, then CTL+SHIFT+P->Run Task: Download Artifact
