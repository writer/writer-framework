import re

from click.testing import CliRunner
from writer.command_line import main

from backend.fixtures.cloud_deploy_fixtures import use_fake_cloud_deploy_server


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

