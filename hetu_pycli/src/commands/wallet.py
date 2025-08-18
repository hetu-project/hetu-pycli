import typer
from web3 import Web3
import os
from rich import print
import getpass
import json
from eth_account import Account

wallet_app = typer.Typer(help="Wallet management commands")


def get_wallet_path(config):
    raw_path = (config or {}).get("wallet_path", "~/.hetucli/wallets")
    return os.path.expanduser(raw_path)


def load_keystore(address_or_name, wallet_path):
    # Support lookup by wallet name or address
    # First try to find by name, otherwise iterate all files to match address field
    file_path = os.path.join(wallet_path, f"{address_or_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    # fallback: iterate all files to find by address
    for f in os.listdir(wallet_path):
        if f.endswith(".json"):
            with open(os.path.join(wallet_path, f), "r") as jf:
                data = json.load(jf)
                if data.get("address", "").lower() == address_or_name.lower():
                    return data
    print(f"[red]Keystore file not found for: {address_or_name}")
    raise typer.Exit(1)


@wallet_app.command()
def create(
    ctx: typer.Context,
    name: str = typer.Option(..., prompt=True, help="Wallet name (used as keystore filename)"),
    password: str = typer.Option(
        None, help="Password for keystore (prompt if not set)"
    ),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
):
    """Create a new wallet and save as keystore file with name"""
    config = ctx.obj
    wallet_path = wallet_path or get_wallet_path(config)
    os.makedirs(wallet_path, exist_ok=True)
    if not password:
        password = getpass.getpass("Set wallet password: ")
    acct = Account.create()
    keystore = Account.encrypt(acct.key, password)
    keystore["name"] = name
    keystore["address"] = acct.address
    keystore_path = os.path.join(wallet_path, f"{name}.json")
    with open(keystore_path, "w") as f:
        json.dump(keystore, f)
    print(f"[green]Address: {acct.address}\nKeystore: {keystore_path}\nName: {name}")


@wallet_app.command()
def unlock(
    ctx: typer.Context,
    name_or_address: str = typer.Argument(..., help="Wallet name or address"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(
        None, help="Password for keystore (prompt if not set)"
    ),
):
    """Unlock a wallet from keystore file and print address"""
    config = ctx.obj
    wallet_path = wallet_path or get_wallet_path(config)
    keystore = load_keystore(name_or_address, wallet_path)
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
    """List all wallet names and addresses in wallet_path"""
    config = ctx.obj
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
        with open(os.path.join(wallet_path, f), "r") as jf:
            data = json.load(jf)
            name = data.get("name", f.replace('.json', ''))
            address = data.get("address", "")
            print(f"  - {name}: {address}")


@wallet_app.command(
    name="export",
)
def export_privkey(
    ctx: typer.Context,
    name_or_address: str = typer.Argument(..., help="Wallet name or address"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(
        None, help="Password for keystore (prompt if not set)"
    ),
):
    """Export the private key of a wallet (use with caution!)"""
    config = ctx.obj
    wallet_path = wallet_path or get_wallet_path(config)
    keystore = load_keystore(name_or_address, wallet_path)
    if not password:
        password = getpass.getpass("Keystore password: ")
    try:
        privkey = Account.decrypt(keystore, password)
        print(f"[red]Private key (hex): {privkey.hex()}")
    except Exception as e:
        print(f"[red]Failed to export private key: {e}")
        raise typer.Exit(1)


@wallet_app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def balance(
    ctx: typer.Context,
    wallet_name: str = typer.Argument(..., help="Wallet name (username)"),
    rpc: str = typer.Option(None, help="Hetu node RPC URL (optional, uses default from config if not provided)"),
):
    """Query address balance by wallet name"""
    config = ctx.obj
    rpc_url = rpc or (config.get("json_rpc") if config else None)
    if not rpc_url:
        print("[red]No RPC URL provided or found in config.")
        raise typer.Exit(1)
    wallet_path = get_wallet_path(config)
    
    # Load keystore by wallet name
    try:
        keystore = load_keystore(wallet_name, wallet_path)
        address = keystore.get("address")
        print(f"[yellow]Wallet '{wallet_name}' address: {address}")
    except Exception:
        print(f"[red]Wallet not found: {wallet_name}")
        raise typer.Exit(1)
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    bal = w3.eth.get_balance(address)
    ether = w3.from_wei(bal, 'ether')
    ether_str = f"{ether:,.18f}".rstrip('0').rstrip('.')
    print(f"[cyan]Balance: {ether_str} HETU")
    print(f"[cyan]Address: {address}")


@wallet_app.command(
    name="import",
)
def import_privkey(
    ctx: typer.Context,
    privkey: str = typer.Argument(..., help="Private key (hex)"),
    name: str = typer.Option(..., prompt=True, help="Wallet name (used as keystore filename)"),
    password: str = typer.Option(
        None, help="Password for keystore (prompt if not set)"
    ),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
):
    """Import a private key and save as keystore file with name"""
    config = ctx.obj
    wallet_path = wallet_path or get_wallet_path(config)
    os.makedirs(wallet_path, exist_ok=True)
    if not password:
        password = getpass.getpass("Set wallet password: ")
    acct = Account.from_key(privkey)
    keystore = Account.encrypt(acct.key, password)
    keystore["name"] = name
    keystore["address"] = acct.address
    keystore_path = os.path.join(wallet_path, f"{name}.json")
    with open(keystore_path, "w") as f:
        json.dump(keystore, f)
    print(f"[green]Imported address: {acct.address}\nKeystore: {keystore_path}\nName: {name}")


@wallet_app.command()
def sign_tx(
    ctx: typer.Context,
    name_or_address: str = typer.Argument(..., help="Wallet name or address"),
    tx: str = typer.Argument(..., help="Raw tx dict as JSON string"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(
        None, help="Password for keystore (prompt if not set)"
    ),
):
    """Sign a raw transaction with keystore, print signed rawTransaction (hex)"""
    config = ctx.obj
    wallet_path = wallet_path or get_wallet_path(config)
    keystore = load_keystore(name_or_address, wallet_path)
    if not password:
        password = getpass.getpass("Keystore password: ")
    try:
        privkey = Account.decrypt(keystore, password)
        acct = Account.from_key(privkey)
        import json as _json
        tx_dict = _json.loads(tx)
        signed = acct.sign_transaction(tx_dict)
        print(f"[cyan]rawTransaction: {signed.rawTransaction.hex()}")
    except Exception as e:
        print(f"[red]Failed to sign transaction: {e}")
        raise typer.Exit(1)