import contextlib
import json
import re
import threading
import time
from datetime import datetime, timedelta
from typing import Annotated

import pytest
import pytz
import uvicorn
from click.testing import CliRunner
from fastapi import Body, Depends, FastAPI, File, Header, UploadFile
from writer.command_line import main


def create_app():
    class State:
        log_counter = 0
        envs: str| None = None

    state = State()
    app = FastAPI()


    @app.post("/deploy")
    def deploy(
        state: Annotated[State, Depends(lambda: state)],
        authorization: Annotated[str, Header(description="The API key")],
        file: UploadFile = File(...),
        envs: Annotated[str, Body(description = 'JSON object of environment variables')] = "{}",
    ):
        print (envs)
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



@pytest.fixture(autouse=True)
def run_with_server():
    server = Server()
    with server.run_in_thread():
        yield 
        print('end')

def assert_warning(result, url = "https://my-app.com"):
    found = re.search(f".WARNING. URL: {url}", result.output)
    
    assert found is not None


def assert_url(result, expectedUrl):
    url = re.search("URL: (.*)$", result.output)
    assert url and url.group(1) == expectedUrl

def extract_envs(result):
    content = re.search("<envs>(.*)</envs>", result.output)
    assert content is not None
    return json.loads(content.group(1))


def test_deploy():
    runner = CliRunner()
    with runner.isolated_filesystem():
        
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, ['cloud', 'deploy', './my_app'], env={
            'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
            'WRITER_API_KEY': 'test',
        }, input='y\n')
        print(result.output)
        assert result.exit_code == 0
        assert_warning(result)
        assert_url(result, 'https://my-app.com')

def test_deploy_force_flag():
    runner = CliRunner()
    with runner.isolated_filesystem():
        
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, ['cloud', 'deploy', './my_app', '--force'], env={
            'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
            'WRITER_API_KEY': 'test',
        })
        print(result.output)
        assert result.exit_code == 0
        found = re.search(".WARNING. URL: https://my-app.com", result.output)
        assert found is None
        assert_url(result, 'https://my-app.com')

def test_deploy_api_key_option():
    runner = CliRunner()
    with runner.isolated_filesystem():
        
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, ['cloud', 'deploy', './my_app', '--api-key', 'test'], env={
            'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
            'WRITER_API_KEY': 'fail',
        }, input='y\n')
        print(result.output)
        assert result.exit_code == 0
        assert_warning(result)
        assert_url(result, 'https://my-app.com')

def test_deploy_api_key_prompt():
    runner = CliRunner()
    with runner.isolated_filesystem():
        
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, ['cloud', 'deploy', './my_app'], env={
            'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
        }, input='test\ny\n')
        print(result.output)
        assert result.exit_code == 0
        assert_warning(result)
        assert_url(result, 'https://my-app.com')

def test_deploy_warning():
    runner = CliRunner()
    with runner.isolated_filesystem():
        
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, ['cloud', 'deploy', './my_app'], env={
            'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
            'WRITER_API_KEY': 'test',
        })
        print(result.output)
        assert result.exit_code == 1

def test_deploy_env():
    runner = CliRunner()
    with runner.isolated_filesystem():
        
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, 
            args = [
                'cloud', 'deploy', './my_app',
                '-e', 'ENV1=test', '-e', 'ENV2=other'
            ], 
            env={
                'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
                'WRITER_API_KEY': 'test',
                'WRITER_DEPLOY_SLEEP_INTERVAL': '0'
            },
            input='y\n'
        )
        print(result.output)
        assert result.exit_code == 0
        envs = extract_envs(result)
        assert envs['ENV1'] == 'test'
        assert envs['ENV2'] == 'other'
        assert_url(result, 'https://my-app.com')

def test_deploy_full_flow():
    runner = CliRunner()
    with runner.isolated_filesystem():
        
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, 
            args = [
                'cloud', 'deploy', './my_app',
                '-e', 'ENV1=test', '-e', 'ENV2=other'
            ], 
            env={
                'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
                'WRITER_API_KEY': 'full',
                'WRITER_DEPLOY_SLEEP_INTERVAL': '0'
            },
        )
        print(result.output)
        assert result.exit_code == 0
        envs = extract_envs(result)
        assert envs['ENV1'] == 'test'
        assert envs['ENV2'] == 'other'
        assert_url(result, 'https://full.my-app.com')

        logs = re.findall("<log[0-9]/>", result.output)
        assert logs[0] == "<log0/>"
        assert logs[1] == "<log1/>"
        assert logs[2] == "<log2/>"
        assert logs[3] == "<log3/>"


def test_undeploy():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, 
            args = [
                'cloud', 'undeploy'
            ], 
            env={
                'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
                'WRITER_API_KEY': 'full',
                'WRITER_DEPLOY_SLEEP_INTERVAL': '0'
            },
        )
        print(result.output)
        assert re.search("App undeployed", result.output)
        assert result.exit_code == 0

