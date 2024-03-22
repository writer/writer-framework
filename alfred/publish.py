"""
The publish module contains the commands to carry out the deployment.

The alfred publish command creates a new tag that triggers the deployment pipeline.
"""
import os
import sys

import alfred
import click
from click import Choice

ROOT_DIR = os.path.realpath(os.path.join(__file__, "..", ".."))

@alfred.command("publish", help="tag a new release and trigger pypi publication")
def publish():
    """
    tag a release of fixtup and release through github actions

    Before running the command, it checks if the branch is on master, if the branch is up to date with origin/master.

    >>> $ alfred publish
    """
    import streamsync
    VERSION = f"v{streamsync.VERSION}"

    git = alfred.sh("git", "git should be present")
    os.chdir(ROOT_DIR)

    # run poetry install to update the version number
    alfred.run("poetry install", stream_stdout=False, stream_stderr=False)

    # update the existing tags
    alfred.run(git, ["fetch"])

    _, stdout, _ = alfred.run(git, ["describe", "--tags", "--abbrev=0"])
    current_version = stdout.strip()

    _, stdout, _ = alfred.run(git, ["status"])
    git_status = stdout.strip()

    on_master = "On branch master" in git_status
    if not on_master:
        click.echo(click.style("Branch should be on master, use git checkout master", fg="red"))
        click.echo(git_status.strip()[0])
        sys.exit(1)

    up_to_date = "Your branch is up to date with 'origin/master'" in git_status
    if not up_to_date:
        click.echo(click.style("Branch should be up to date with origin/master, push your change to repository", fg="red"))
        sys.exit(1)

    non_commited_changes = "Changes not staged for commit" in git_status or "Changes to be committed" in git_status
    if non_commited_changes:
        click.echo(click.style("Changes in progress, can't release a new version", fg="red"))
        sys.exit(1)

    if current_version == VERSION:
        click.echo(click.style(f"Version {VERSION} already exists, update version in pyproject.toml", fg='red'))
        sys.exit(1)

    click.echo("")
    click.echo(f"Next release {VERSION} (current: {current_version})")
    click.echo("")
    value = click.prompt("Confirm", type=Choice(['y', 'n']), show_choices=True, default='n')

    if value == 'y':
        alfred.run(git, ['tag', VERSION])
        alfred.run(git, ['push', 'origin', VERSION])


@alfred.command("publish.pypi", help="publish the package on pypi", hidden=True)
def publish_pypi():
    """
    publish the package on pypi using poetry. This command is run with github actions.

    You can run it from local. You should set PYPI_TOKEN environment variable with your pypi token
    to run it in local.
    """
    pypi_token = os.getenv('PYPI_TOKEN', None)
    if pypi_token is not None:
        alfred.run(f"poetry config pypi-token.pypi {pypi_token}")
        alfred.run("poetry publish --build")
    else:
        click.echo(click.style("PYPI_TOKEN is not set as environment variable", fg='red'))
        sys.exit(1)
