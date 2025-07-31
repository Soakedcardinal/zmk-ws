# zmk-ws


create an .env file with:
```.env
GITHUB_TOKEN=your_token
GITHUB_OWNER=your_username_or_org
GITHUB_REPO=your_repo_name
```

```powershell
python .\build.py

python .\download_artifact.py
```

or use vscode/vscodium, CTL+SHIFT+B to build, then CTL+SHIFT+P->Run Task: Download Artifact