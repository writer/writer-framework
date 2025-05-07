name: ci

on:
  push:
    branches:
      - 'trigger-test'

jobs:
  build:
    runs-on: ubuntu-latest

    - name: Trigger agent manager
      run: |
        repo_owner="writer"
        repo_name="be.agent-manager"
        event_type="trigger-workflow"

        curl -L \
          -X POST \
          -H "Accept: application/vnd.github+json" \
          -H "Authorization: Bearer ${{ secrets.AGENT_MANAGER_PAT }}" \
          -H "X-GitHub-Api-Version: 2022-11-28" \
          https://api.github.com/repos/$repo_owner/$repo_name/dispatches \
          -d "{\"event_type\": \"$event_type\", \"client_payload\": {\"unit\": false, \"integration\": true}}"
