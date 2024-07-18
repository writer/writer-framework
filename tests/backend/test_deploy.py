import json
import re

from click.testing import CliRunner
from writer.command_line import main

from backend.fixtures.cloud_deploy_fixtures import use_fake_cloud_deploy_server 


def _assert_warning(result, url = "https://my-app.com"):
    found = re.search(f".WARNING. URL: {url}", result.output)
    
    assert found is not None


def _assert_url(result, expectedUrl):
    url = re.search("URL: (.*)$", result.output)
    assert url and url.group(1) == expectedUrl

def _extract_envs(result):
    content = re.search("<envs>(.*)</envs>", result.output)
    assert content is not None
    return json.loads(content.group(1))


def test_deploy():
    runner = CliRunner()
    with runner.isolated_filesystem(), use_fake_cloud_deploy_server():
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, ['cloud', 'deploy', './my_app'], env={
            'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
            'WRITER_API_KEY': 'test',
        }, input='y\n')
        print(result.output)
        assert result.exit_code == 0
        _assert_warning(result)
        _assert_url(result, 'https://my-app.com')

def test_deploy_force_flag():
    runner = CliRunner()
    with runner.isolated_filesystem(), use_fake_cloud_deploy_server():
        
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
        _assert_url(result, 'https://my-app.com')

def test_deploy_api_key_option():
    runner = CliRunner()
    with runner.isolated_filesystem(), use_fake_cloud_deploy_server():
        
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, ['cloud', 'deploy', './my_app', '--api-key', 'test'], env={
            'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
            'WRITER_API_KEY': 'fail',
        }, input='y\n')
        print(result.output)
        assert result.exit_code == 0
        _assert_warning(result)
        _assert_url(result, 'https://my-app.com')

def test_deploy_api_key_prompt():
    runner = CliRunner()
    with runner.isolated_filesystem(), use_fake_cloud_deploy_server():
        
        result = runner.invoke(main, ['create', './my_app'])
        assert result.exit_code == 0
        result = runner.invoke(main, ['cloud', 'deploy', './my_app'], env={
            'WRITER_DEPLOY_URL': 'http://localhost:8888/deploy',
        }, input='test\ny\n')
        print(result.output)
        assert result.exit_code == 0
        _assert_warning(result)
        _assert_url(result, 'https://my-app.com')

def test_deploy_warning():
    runner = CliRunner()
    with runner.isolated_filesystem(), use_fake_cloud_deploy_server():
        
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
    with runner.isolated_filesystem(), use_fake_cloud_deploy_server():
        
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
        envs = _extract_envs(result)
        assert envs['ENV1'] == 'test'
        assert envs['ENV2'] == 'other'
        _assert_url(result, 'https://my-app.com')

def test_deploy_full_flow():
    runner = CliRunner()
    with runner.isolated_filesystem(), use_fake_cloud_deploy_server():
        
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
        envs = _extract_envs(result)
        assert envs['ENV1'] == 'test'
        assert envs['ENV2'] == 'other'
        _assert_url(result, 'https://full.my-app.com')

        logs = re.findall("<log[0-9]/>", result.output)
        assert logs[0] == "<log0/>"
        assert logs[1] == "<log1/>"
        assert logs[2] == "<log2/>"
        assert logs[3] == "<log3/>"


def test_undeploy():
    runner = CliRunner()
    with runner.isolated_filesystem(), use_fake_cloud_deploy_server():
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

