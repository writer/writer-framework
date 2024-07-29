import os

import alfred


@alfred.command("run.docs", help="preview the documentation as a developper")
def run_docs():
    os.chdir('docs')
    alfred.run("npm run preview")

@alfred.command("run.storybook", help="preview the storybook as a developper")
def run_storybook():
    os.chdir('src/ui')
    alfred.run("npm run storybook")
