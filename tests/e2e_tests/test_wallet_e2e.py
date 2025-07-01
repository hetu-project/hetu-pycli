import subprocess
import sys
import os
import tempfile
# import shutil
import pytest

CLI = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../hetu_pycli/cli.py")
)


@pytest.mark.skipif(not os.path.exists(CLI), reason="CLI entry not found")
def test_wallet_create_and_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create wallet
        name = "testwallet"
        password = "testpass"
        result = subprocess.run(
            [
                sys.executable,
                CLI,
                "wallet",
                "create",
                "--name",
                name,
                "--password",
                password,
                "--wallet-path",
                tmpdir,
            ],
            capture_output=True,
            text=True,
            input="\n",
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        assert result.returncode == 0
        assert "Address:" in result.stdout
        # List wallets
        result2 = subprocess.run(
            [sys.executable, CLI, "wallet", "list", "--wallet-path", tmpdir],
            capture_output=True,
            text=True,
        )
        assert result2.returncode == 0
        assert name in result2.stdout


@pytest.mark.skipif(not os.path.exists(CLI), reason="CLI entry not found")
def test_wallet_import_export_unlock():
    with tempfile.TemporaryDirectory() as tmpdir:
        name = "testimport"
        password = "testpass"
        privkey = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        # Import private key
        result = subprocess.run(
            [
                sys.executable,
                CLI,
                "wallet",
                "import",
                privkey,
                "--name",
                name,
                "--password",
                password,
                "--wallet-path",
                tmpdir,
            ],
            capture_output=True,
            text=True,
            input="\n",
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        assert result.returncode == 0
        assert "Imported address:" in result.stdout
        # Export private key
        result2 = subprocess.run(
            [
                sys.executable,
                CLI,
                "wallet",
                "export",
                name,
                "--password",
                password,
                "--wallet-path",
                tmpdir,
            ],
            capture_output=True,
            text=True,
        )
        assert result2.returncode == 0
        assert "Private key (hex):" in result2.stdout
        assert privkey.lower().replace("0x", "") in result2.stdout.lower().replace(
            "0x", ""
        )
        # Unlock wallet
        result3 = subprocess.run(
            [
                sys.executable,
                CLI,
                "wallet",
                "unlock",
                name,
                "--password",
                password,
                "--wallet-path",
                tmpdir,
            ],
            capture_output=True,
            text=True,
        )
        assert result3.returncode == 0
        assert "Unlocked address:" in result3.stdout
