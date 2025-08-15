import typer
from rich import print
from web3 import Web3
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path

hetu_app = typer.Typer(help="Native HETU operations")

@hetu_app.command()
def balance_of(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Wallet name or address to query"),
):
    """Query native HETU balance of an account"""
    config = ctx.obj
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    address = name
    wallet_path = get_wallet_path(config)
    if not (address.startswith('0x') and len(address) == 42):
        try:
            keystore = load_keystore(name, wallet_path)
            address = keystore.get("address")
        except Exception:
            print(f"[red]Wallet not found: {name}")
            raise typer.Exit(1)
    
    provider = Web3.HTTPProvider(rpc)
    web3 = Web3(provider)
    balance_wei = web3.eth.get_balance(address)
    balance_hetu = web3.from_wei(balance_wei, "ether")
    print(f"[green]Native HETU Balance: {balance_hetu} HETU")
    print(f"[yellow]Raw balance: {balance_wei} wei") 