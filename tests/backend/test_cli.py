import os

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
        #check if filder exists and if has the right files
        assert os.path.exists('./my_app')
        assert os.path.exists('./my_app/ui.json')
        assert os.path.exists('./my_app/main.py')
        #load toml and check name and version
        with open('./my_app/pyproject.toml') as f:
            content = f.read()
        assert content.find('name = "writer-framework-default"') != -1

def test_create_specific_template():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['create', './my_app', '--template', 'hello'])
        print(result.output)
        assert result.exit_code == 0
        #check if filder exists and if has the right files
        assert os.path.exists('./my_app')
        assert os.path.exists('./my_app/ui.json')
        assert os.path.exists('./my_app/main.py')
        #load toml and check name and version
        with open('./my_app/pyproject.toml') as f:
            content = f.read()
        assert content.find('name = "writer-framework-hello"') != -1
