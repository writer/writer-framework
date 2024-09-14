import os

from writer import wf_project

import alfred


@alfred.command('apps.update', help='update the apps in the repo to the latest version')
@alfred.option('--app', help='the path of the app to update')
def apps_update(app: str = None):
    import writer

    if app is not None:
        apps = [app]
    else:
        apps = [
            'apps/ai-starter',
            'apps/default',
            'apps/hello',
            'apps/pdg-tutorial',
            'apps/quickstart',
            'apps/text-demo',
            'tests/backend/testapp',
            'tests/backend/testbasicauth',
            'tests/backend/testmultiapp/app1',
            'tests/backend/testmultiapp/app2',
        ]

    for app in apps:
        abs_path = os.path.realpath(app)
        if not os.path.isdir(abs_path):
            continue

        if os.path.isfile(os.path.join(abs_path, "ui.json")):
            print(f'{app} : migrate ui.json')
            wf_project.migrate_obsolete_ui_json(abs_path)

        metadata, components = wf_project.read_files(abs_path)
        if metadata.get('writer_version') == writer.VERSION:
            print("The app is already up to date")
        else:
            metadata['writer_version'] = writer.VERSION
            wf_project.write_files(abs_path, metadata, components)
            print(f"{app} : app is up to date")
