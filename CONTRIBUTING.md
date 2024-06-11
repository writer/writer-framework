# Contributing to Writer Framework

Thank you for your interest in contributing to Writer Framework.

## Ways to contribute

Beyond contributing to the repository, some ways to contribute to this project include:

- _Reporting bugs_. Bug reports are relatively easy to write, but have a big impact. Please include the steps required to reproduce the bug. Use "Issues" on GitHub. This is an example of a [wonderful bug report](https://github.com/streamsync-cloud/streamsync/issues/24).
- _Creating content_. Think articles or tutorials. It doesn't have to be overwhelmingly positive; constructive criticism is appreciated. A great example is [this review](https://jreyesr.github.io/posts/streamsync-review/). A YouTube tutorial would be fantastic!
- _Browse Issues and Discussions_. Browse these sections on GitHub and see if you can help.
- _Suggesting valuable enhancements_. If you think of a feature that can have a positive impact, suggest it. Please use the "Discussions" on GitHub.
- _Sponsoring the project_. Helps offset hosting and other expenses.
- _Promoting the project_. Star it, share on LinkedIn or other social media.

## Contributing to the repository

If you wish to contribute to the repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change. Failure to discuss the changes beforehand will likely cause your pull request to be rejected, regrettably.

Make sure to run the tests, which can be found in `/tests`, and pass mypy validation. Code formatting is important; Prettier is used in the frontend while autopep8 is used in the backend.

Pull requests should be done on the `dev` branch. When the release is finalised, `dev` will be merged into `master`.

## Setting up a development environment

Whether you're interested in contributing to the repository, creating a fork, or just improving your understanding of Writer Framework, these are the suggested steps for setting up a development environment.

- You can install the package in editable mode using `poetry install`
- Enable the virtual environment with `poetry shell`
- Install all the dev dependencies with `alfred install.dev`
- Run Writer Framework on port 5000. For example, `writer edit apps/hello --port 5000`.
