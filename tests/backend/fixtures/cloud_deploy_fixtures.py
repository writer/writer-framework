import contextlib
import json
import re
import threading
import time
from datetime import datetime, timedelta
from typing import Annotated, Union

import pytest
import pytz
import uvicorn
from click.testing import CliRunner
from fastapi import Body, Depends, FastAPI, File, Header, UploadFile
from writer.command_line import main




def create_app():
    class State:
        log_counter = 0
        envs: Union[str, None] = None

    state = State()
    app = FastAPI()


    @app.post("/deploy")
    def deploy(
        state: Annotated[State, Depends(lambda: state)],
        authorization: Annotated[str, Header(description="The API key")],
        file: UploadFile = File(...),
        envs: Annotated[str, Body(description = 'JSON object of environment variables')] = "{}",
    ):
        state.envs = envs
        return {"status": "ok", "buildId": "123"}


    @app.get("/deploy")
    def get_status(
        state: Annotated[State, Depends(lambda: state)],
        authorization: Annotated[str, Header(description="The API key")],
    ):

        def get_time(n):
            return (datetime.now(pytz.timezone('UTC')) + timedelta(seconds=n)).isoformat()

        state.log_counter += 1
        if (authorization == "Bearer full"):
            if state.log_counter == 1: # first call is to checking if app exist
                return {
                    "logs": [],
                    "status": {
                        "url": None,
                        "status": "PENDING",
                    }
                }
            if state.log_counter == 2:
                return {
                    "logs": [
                        {"log": f"{get_time(-7)} stdout F <envs>{state.envs}</envs>"},
                        {"log": f"{get_time(-6)} stdout F <log0/>"},
                        {"log": f"{get_time(-5)} stdout F <log1/>"},
                    ],
                    "status": {
                        "url": None,
                        "status": "BUILDING",
                    }
                }
            if state.log_counter == 3:
                return {
                    "logs": [
                        {"log": f"{get_time(-2)} stdout F <log3/>"},
                        {"log": f"{get_time(-4)} stdout F <log2/>"},
                    ],
                    "status": {
                        "url": "https://full.my-app.com",
                        "status": "COMPLETED",
                    }
                }
        if (authorization == "Bearer test"):
            return {
                "logs": [
                    {"log": f"20210813163223 stdout F <envs>{state.envs}</envs>"},
                ],
                "status": {
                    "url": "https://my-app.com",
                    "status": "COMPLETED",
                }
            }
        return {
            "logs": [],
            "status": {
                "url": None,
                "status": "FAILED",
            }
        }

    @app.delete("/deploy")
    def undeploy(
        authorization: Annotated[str, Header(description="The API key")],
    ):
        return {"status": "ok"}
    return app


class Server(uvicorn.Server):
    def __init__(self):
        config = uvicorn.Config(create_app(), host="127.0.0.1", port=8888, log_level="info")
        super().__init__(config)
        self.keep_running = True

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()



@contextlib.contextmanager
def use_fake_cloud_deploy_server():
    server = Server()
    with server.run_in_thread():
        yield server
