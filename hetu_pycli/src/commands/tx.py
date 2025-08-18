import typer
from web3 import Web3
from eth_account import Account
from rich import print
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path
import getpass

tx_app = typer.Typer(help="Transfer and transaction commands")

@tx_app.command()
def send(
    ctx: typer.Context,
    sender: str = typer.Option(..., help="Wallet name or address (local keystore)"),
    to: str = typer.Option(..., help="Recipient address"),
    value: float = typer.Option(..., help="Transfer amount (HETU)"),
    rpc: str = typer.Option(None, help="Ethereum node RPC URL (optional, uses default from config if not provided)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, help="Password for keystore (prompt if not set)"),
):
    """Send HETU transfer using local keystore by wallet name or address."""
    config = getattr(ctx, "obj", None) or {}
    rpc_url = rpc or config.get("json_rpc")
    if not rpc_url:
        print("[red]No RPC URL provided or found in config.")
        raise typer.Exit(1)
    wallet_path = wallet_path or get_wallet_path(config)
    keystore = load_keystore(sender, wallet_path)
    if not password:
        password = getpass.getpass("Keystore password: ")
    try:
        privkey = Account.decrypt(keystore, password)
        acct = Account.from_key(privkey)
    except Exception as e:
        print(f"[red]Failed to unlock keystore: {e}")
        raise typer.Exit(1)
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = {
        "to": to,
        "value": w3.to_wei(value, "ether"),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
    }
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Transaction sent: {tx_hash.hex()}")


@tx_app.command(name="send-dk")
def send_by_direct_key(
    ctx: typer.Context,
    private_key: str = typer.Option(..., help="Sender private key"),
    to: str = typer.Option(..., help="Recipient address"),
    value: float = typer.Option(..., help="Transfer amount (HETU)"),
    rpc: str = typer.Option(None, help="Ethereum node RPC URL (optional, uses default from config if not provided)"),
):
    """Send HETU transfer directly by private key."""
    config = getattr(ctx, "obj", {}) or {}
    rpc_url = rpc or config.get("json_rpc")
    if not rpc_url:
        print("[red]No RPC URL provided or found in config.")
        raise typer.Exit(1)
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    acct = Account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = {
        "to": to,
        "value": w3.to_wei(value, "ether"),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
    }
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Transaction sent: {tx_hash.hex()}")