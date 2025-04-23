import os

import alfred


@alfred.command("run.storybook", help="preview the storybook as a developper")
def run_storybook():
    os.chdir("src/ui")
    alfred.run("npm run storybook")
