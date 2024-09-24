import json
import logging
from typing import Any, List, Tuple

import requests

import alfred


@alfred.command("github.notify-changes-doc")
@alfred.option("--remote", default="origin")
@alfred.option("--branch", default="dev")
@alfred.option("--commit", default="HEAD")
@alfred.option("--dry", is_flag=True)
@alfred.option("--slack-webhook", default=None)
def notify_doc_changes(remote: str, branch: str, commit: str, dry: bool, slack_webhook: str = None):
    logger = logging.getLogger("alfred")
    logger.setLevel(logging.INFO)
    logger.info(f"remote: {remote}, branch: {branch}, commit: {commit}, dry: {dry}")

    sections = {
        'components': [
            'src/components/core/content',
            'src/components/core/embed',
            'src/components/core/input',
            'src/components/core/layout',
            'src/components/core/other',
            'src/components/core/root',
        ],
        'documentation': [
            'docs/framework',
        ],
    }

    if commit == "HEAD":
        _, stdout, _ = alfred.run("git rev-parse HEAD")
        commit = stdout.strip()

    all_change_types = ['A', 'M', 'D']

    file_changes: List[Tuple[str, str]] = []
    component_added: List[Tuple[str, str]] = []
    documentation_changes: List[Tuple[str, str]] = []
    alfred.run(f"git fetch {remote} {branch}")

    for change in all_change_types:
        _, stdout, _ = alfred.run(f"git diff --name-only --diff-filter={change} {commit}^ {commit}")
        file_changes += [(f, change) for f in stdout.splitlines() if f.strip() != ""]

    file_changes = sorted(file_changes, key=lambda x: x[0])
    for change in all_change_types:
        for f in [f for f, _change in file_changes if _change == change]:
            for path in sections['documentation']:
                if f.startswith(path):
                    documentation_changes.append((f, change))

    for change in ['A']:
        for f in [f for f, _change in file_changes if _change == change]:
            for path in sections['components']:
                if f.startswith(path):
                    component_added.append((f, 'A'))

    logger.info(f"Documentation changes: {documentation_changes}")
    logger.info(f"Component added: {component_added} - not used yet")

    if dry is None:
        message_documentations = _build_slack_message_documentation(documentation_changes, commit)
        if len(message_documentations) > 0:
            msg = {}
            msg['blocks'] = []
            msg['blocks'] += message_documentations
            response = requests.post(
                slack_webhook, data=json.dumps(msg),
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                print('Message sent successfully')
            else:
                print(f'Failed to send message. Error code : {response.status_code}')
        else:
            print('No documentation changes to notify')
    else:
        print(json.dumps(documentation_changes, indent=2))


def _build_slack_message_documentation(changes: List[Tuple[str, str]], commit: str) -> List[Any]:
    if len(changes) == 0:
        return []

    message: List[Any] = []
    message.append({
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": "Writer framework | Documentation changes",
        }
    })

    workflows = [
        ('A', 'added page', 'Open'),
        ('M', 'modified page', 'Compare'),
        ('D', 'deleted page', 'Open'),
    ]

    for workflow in workflows:
        changes_modified = [f for f, change in changes if change == workflow[0]]
        if len(changes_modified) > 0:
            message.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": workflow[1]
                    }
                ]
            })

            for file in changes_modified:
                message.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"`{file}`"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": workflow[2],
                        },
                        "url": f"https://github.com/writer/writer-framework/commit/{commit}/{file}",
                    }
                })

    return message

