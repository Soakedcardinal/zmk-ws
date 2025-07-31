# zmk-ws

https://zmk.dev/docs/development/hardware-integration/physical-layouts
https://zmk-physical-layout-converter.streamlit.app/
https://zmk-layout-helper.netlify.app/


winget install --id GitHub.cli
gh auth login

gh run download $(gh run list --limit 1 --json databaseId --jq '.[0].databaseId') --dir release