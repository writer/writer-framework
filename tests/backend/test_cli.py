import ctypes
import os
import subprocess
import threading
import time

import requests
from click.testing import CliRunner
from writer.command_line import main


def test_version():
   runner = CliRunner()
   with runner.isolated_filesystem():
      result = runner.invoke(main, ['-v'])
      assert result.exit_code == 0
      assert 'version' in result.output

def test_create_default():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['create', './my_app'])
        print(result.output)
        assert result.exit_code == 0
        assert os.path.exists('./my_app')
        assert os.path.exists('./my_app/ui.json')
        assert os.path.exists('./my_app/main.py')
        with open('./my_app/pyproject.toml') as f:
            content = f.read()
        assert content.find('name = "writer-framework-default"') != -1

def test_create_specific_template():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['create', './my_app', '--template', 'hello'])
        print(result.output)
        assert result.exit_code == 0
        assert os.path.exists('./my_app')
        assert os.path.exists('./my_app/ui.json')
        assert os.path.exists('./my_app/main.py')
        with open('./my_app/pyproject.toml') as f:
            content = f.read()
        assert content.find('name = "writer-framework-hello"') != -1


def test_run():
    runner = CliRunner()
    p = None
    try:
        with runner.isolated_filesystem():
            runner.invoke(main, ['create', './my_app', '--template', 'hello'])
            p = subprocess.Popen(["writer run my_app --port 5001"], shell=True)

            retry = 0
            success = False
            while True:
                try:
                    response = requests.get('http://127.0.0.1:5001')
                    if response.status_code == 200:
                        success = True
                        break
                    if response.status_code != 200:
                        raise Exception("Status code is not 200")
                except Exception:
                    time.sleep(1)
                    retry += 1
                    if retry > 10:
                        break
            assert success == True
    finally:
        if p is not None:
            p.terminate()


def test_edit():
    runner = CliRunner()
    p = None
    try:
        with runner.isolated_filesystem():
            runner.invoke(main, ['create', './my_app', '--template', 'hello'])
            p = subprocess.Popen(["writer edit my_app --port 5002"], shell=True)

            retry = 0
            success = False
            while True:
                try:
                    response = requests.get('http://127.0.0.1:5002')
                    if response.status_code == 200:
                        success = True
                        break
                    if response.status_code != 200:
                        raise Exception("Status code is not 200")
                except Exception:
                    retry += 1
                    time.sleep(1)
                    if retry > 10:
                        break
            assert success == True
    finally:
        if p is not None:
            p.terminate()
