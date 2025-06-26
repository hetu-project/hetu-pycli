import typer
from web3 import Web3
import os
from rich import print
import getpass
import json
from eth_account import Account

wallet_app = typer.Typer(help="Wallet management commands")


def get_wallet_path(config):
    return config.get("wallet_path", os.path.expanduser("~/.hetucli/wallets"))


def load_keystore(address, wallet_path):
    keystore_path = os.path.join(wallet_path, f"{address}.json")
    if not os.path.exists(keystore_path):
        print(f"[red]Keystore file not found: {keystore_path}")
        raise typer.Exit(1)
    with open(keystore_path, "r") as f:
        return json.load(f)


@wallet_app.command()
def create(
    ctx: typer.Context,
    password: str = typer.Option(
        None, help="Password for keystore (prompt if not set)"
    ),
):
    """Create a new wallet and save as keystore file"""
    config = getattr(ctx, "obj", {}) or {}
    wallet_path = get_wallet_path(config)
    os.makedirs(wallet_path, exist_ok=True)
    if not password:
        password = getpass.getpass("Set wallet password: ")
    acct = Account.create()
    keystore = Account.encrypt(acct.key, password)
    address = acct.address
    keystore_path = os.path.join(wallet_path, f"{address}.json")
    with open(keystore_path, "w") as f:
        json.dump(keystore, f)
    print(f"[green]Address: {address}\nKeystore: {keystore_path}")


@wallet_app.command()
def unlock(
    ctx: typer.Context,
    address: str = typer.Argument(..., help="Wallet address"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(
        None, help="Password for keystore (prompt if not set)"
    ),
):
    """Unlock a wallet from keystore file and print address"""
    config = getattr(ctx, "obj", {}) or {}
    wallet_path = wallet_path or get_wallet_path(config)
    keystore = load_keystore(address, wallet_path)
    if not password:
        password = getpass.getpass("Keystore password: ")
    try:
        acct = Account.decrypt(keystore, password)
        acct_obj = Account.from_key(acct)
        print(f"[green]Unlocked address: {acct_obj.address}")
    except Exception as e:
        print(f"[red]Failed to unlock wallet: {e}")
        raise typer.Exit(1)


@wallet_app.command()
def list(
    ctx: typer.Context,
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
):
    """List all wallet addresses in wallet_path"""
    config = getattr(ctx, "obj", {}) or {}
    wallet_path = wallet_path or get_wallet_path(config)
    if not os.path.exists(wallet_path):
        print(f"[yellow]No wallet directory found: {wallet_path}")
        return
    files = [f for f in os.listdir(wallet_path) if f.endswith(".json")]
    if not files:
        print(f"[yellow]No keystore files found in {wallet_path}")
        return
    print(f"[cyan]Wallets in {wallet_path}:")
    for f in files:
        print(f"  - {f.replace('.json', '')}")


@wallet_app.command()
def export_privkey(
    ctx: typer.Context,
    address: str = typer.Argument(..., help="Wallet address"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(
        None, help="Password for keystore (prompt if not set)"
    ),
):
    """Export the private key of a wallet (use with caution!)"""
    config = getattr(ctx, "obj", {}) or {}
    wallet_path = wallet_path or get_wallet_path(config)
    keystore = load_keystore(address, wallet_path)
    if not password:
        password = getpass.getpass("Keystore password: ")
    try:
        privkey = Account.decrypt(keystore, password)
        print(f"[red]Private key (hex): {privkey.hex()}")
    except Exception as e:
        print(f"[red]Failed to export private key: {e}")
        raise typer.Exit(1)


@wallet_app.command()
def balance(address: str, rpc: str = typer.Option(..., help="Hetu node RPC URL")):
    """Query address balance"""
    w3 = Web3(Web3.HTTPProvider(rpc))
    bal = w3.eth.get_balance(address)
    print(f"[cyan]Balance: {w3.from_wei(bal, 'ether')} ETH")
