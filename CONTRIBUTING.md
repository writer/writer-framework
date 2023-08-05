# Contributing to Streamsync

Thank you for your interest in contributing to Streamsync.

## Ways to contribute

Beyond contributing to the repository, some ways to contribute to this project include: 

- *Reporting bugs*. Bug reports are relatively easy to write, but have a big impact. Please include the steps required to reproduce the bug. Use "Issues" on GitHub. This is an example of a [wonderful bug report](https://github.com/streamsync-cloud/streamsync/issues/24).
- *Creating content*. Think articles or tutorials. It doesn't have to be overwhelmingly positive; constructive criticism is appreciated. A great example is [this review](https://jreyesr.github.io/posts/streamsync-review/). A YouTube tutorial would be fantastic!
- *Browse Issues and Discussions*. Browse these sections on GitHub and see if you can help.
- *Suggesting valuable enhancements*. If you think of a feature that can have a positive impact, suggest it. Please use the "Discussions" on GitHub.
- *Sponsoring the project*. Helps offset hosting and other expenses.
- *Promoting the project*. Star it, share on LinkedIn or other social media.

## Contributing to the repository

If you wish to contribute to the repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change. Failure to discuss the changes beforehand will likely cause your pull request to be rejected, regrettably.

Make sure to run the tests, which can be found in `/tests`, and pass mypy validation. Code formatting is important; Prettier is used in the frontend while autopep8 is used in the backend.

Pull requests should be done on the `dev` branch. When the release is finalised, `dev` will be merged into `master`.

## Setting up a development environment

Whether you're interested in contributing to the repository, creating a fork, or just improving your understanding of Streamsync, these are the suggested steps for setting up a development environment.
- Install streamsync[test] or streamsync[build].
- You can install the package in editable mode using `pip install -e .`, which will make it more convenient if you intend to tweak the backend.
- Run streamsync in port 5000. For example, `streamsync edit hello --port 5000`.
- Install dependencies and run `npm run dev` in `/ui`. This runs the frontend for Streamsync in development mode while proxying requests to port 5000.
- A breakdown of the steps required for packaging can be found in `./build.sh`. Notably, it includes compiling the frontend and taking it from `/ui` and into the Python package.