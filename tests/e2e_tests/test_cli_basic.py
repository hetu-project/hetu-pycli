import subprocess
import sys
import os
import pytest

CLI = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../hetu_pycli/cli.py")
)


@pytest.mark.skipif(not os.path.exists(CLI), reason="CLI entry not found")
def test_cli_help():
    result = subprocess.run(
        [sys.executable, CLI, "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Hetu chain command line client" in result.stdout
