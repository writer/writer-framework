import os

import alfred


@alfred.command("docs.preview", help="preview the documentation as a developper")
def docs_preview():
    os.chdir('docs')
    alfred.run("npm run dev")


@alfred.command("docs.build", help="build the documentation as static files")
def docs_build():
    os.chdir('docs')
    alfred.run("npm run build")
