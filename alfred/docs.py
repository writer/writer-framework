import alfred


@alfred.command('docs.build', help="build documentation")
def docs_build():
    alfred.run("npm run docs:build")

@alfred.command('docs.dev', help="start documentation dev server with hot reloading")
def docs_dev():
    alfred.run("npm run docs:dev")

@alfred.command('docs.preview', help="preview documentation")
def docs_preview():
    alfred.run("npm run docs:preview")
