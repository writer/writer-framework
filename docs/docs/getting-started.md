# Getting started

## Installation and Quickstart

It works on Linux, Mac and Windows. Python 3.9.2 or higher is required.

```sh
pip install "streamsync[ds]"
streamsync hello
```

- The first command will install Streamsync using `pip` and include the optional data science dependencies.
- The second command will create a demo application in the subfolder "hello" and start Streamsync Builder, the framework's visual editor, which will be accessible via a local URL.

We recommend using a virtual environment.

## Create an app

You can use the command `streamsync create`, which will create a placeholder app in the path provided.

```sh
streamsync create [path]

# Creates a new app in folder "testapp"
streamsync create testapp
```

A Streamsync app is a folder with the following items.

- `main.py`. The entry point for the app. You can import anything you need from here.
- `ui.json`. Contains the UI component declarations. Maintained by Builder, the framework's visual editor.
- `static/`. This folder contains frontend-facing static files which you might want to distribute with your app. For example, images.

## Start the editor

You can use the command `streamsync edit`.

```sh
streamsync edit [path]

# Edit the application in subfolder "testapp"
streamsync edit testapp
```

This command will provide you with a local URL which you can use to access Builder.

::: warning Streamsync Builder shouldn't be directly exposed to the Internet.

It's not safe and it won't work, as requests from non-local origins are rejected.

If you need to access Builder remotely, we recommend setting up a SSH tunnel.
:::

## Run an app

When your app is ready, execute the `run` command, which will allow others to run, but not edit, your Streamsync app.

```sh
streamsync run my_app
```

You can specify a port and host. Specifying `--host 0.0.0.0` enables you to share your application in your local network.

```sh
streamsync run my_app --port 5000 --host 0.0.0.0
```

## Running as a module

If you need to run Streamsync as a module, you can use the `streamsync.command_line` module.

```sh
python -m streamsync.command_line run my_app
```