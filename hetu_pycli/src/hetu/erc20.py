import typer
from rich import print
from web3 import Web3
import json
import os
from hetu_pycli.src.hetu.wrapper.erc20 import Erc20
from eth_account import Account
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path
import getpass

ERC20_ABI_PATH = os.path.join(
    os.path.dirname(__file__), "../../../contracts/ERC20MinterBurnerDecimals.abi"
)

erc20_app = typer.Typer(help="ERC20 contract operations")


def load_erc20(contract: str, rpc: str):
    abi_path = os.path.abspath(ERC20_ABI_PATH)
    if not os.path.exists(abi_path):
        print(f"[red]ABI file not found: {abi_path}")
        raise typer.Exit(1)
    with open(abi_path, "r") as f:
        abi = json.load(f)
    provider = Web3.HTTPProvider(rpc)
    return Erc20(contract, provider, abi)


@erc20_app.command()
def balance_of(
    ctx: typer.Context,
    contract: str = typer.Option(..., help="ERC20 contract address"),
    account: str = typer.Option(..., help="Account address to query"),
):
    """Query ERC20 token balance of an account"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    erc20 = load_erc20(contract, rpc)
    balance = erc20.balanceOf(account)
    decimals = erc20.decimals()
    value = balance / (10 ** decimals)
    value_str = f"{value:,.{decimals}f}".rstrip('0').rstrip('.')
    print(f"[green]Balance: {value_str} (raw: {balance}, decimals: {decimals})")


@erc20_app.command()
def transfer(
    ctx: typer.Context,
    contract: str = typer.Option(..., help="ERC20 contract address"),
    to: str = typer.Option(..., help="Recipient address"),
    value: float = typer.Option(..., help="Amount to transfer (human readable, e.g. 1.23)"),
    sender: str = typer.Option(
        ..., help="Sender address (must match keystore address or wallet name)"
    ),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(
        None, hide_input=True, help="Keystore password"
    ),
):
    """Transfer ERC20 tokens, sign and broadcast using local keystore (by wallet name or address)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    config = ctx.obj
    wallet_path = wallet_path or get_wallet_path(config)
    keystore = load_keystore(sender, wallet_path)
    if not password:
        password = getpass.getpass("Keystore password: ")
    try:
        private_key = Account.decrypt(keystore, password)
    except Exception as e:
        print(f"[red]Failed to decrypt keystore: {e}")
        raise typer.Exit(1)
    erc20 = load_erc20(contract, rpc)
    decimals = erc20.decimals()
    value_raw = int(value * (10 ** decimals))
    nonce = erc20.web3.eth.get_transaction_count(keystore["address"])
    tx = erc20.contract.functions.transfer(to, value_raw).build_transaction(
        {
            "from": keystore["address"],
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": erc20.web3.eth.gas_price,
        }
    )
    signed = erc20.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = erc20.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted tx hash: {tx_hash.hex()}")


@erc20_app.command()
def approve(
    ctx: typer.Context,
    contract: str = typer.Option(..., help="ERC20 contract address"),
    spender: str = typer.Option(..., help="Spender address"),
    value: float = typer.Option(..., help="Amount to approve (human readable, e.g. 1.23)"),
    sender: str = typer.Option(
        ..., help="Sender address (must match keystore address or wallet name)"
    ),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(
        None, prompt=True, hide_input=True, help="Keystore password"
    ),
):
    """Approve ERC20 allowance, sign and broadcast using local keystore (by wallet name or address)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    config = ctx.obj
    wallet_path = wallet_path or get_wallet_path(config)
    keystore = load_keystore(sender, wallet_path)
    if not password:
        password = getpass.getpass("Keystore password: ")
    try:
        private_key = Account.decrypt(keystore, password)
    except Exception as e:
        print(f"[red]Failed to decrypt keystore: {e}")
        raise typer.Exit(1)
    erc20 = load_erc20(contract, rpc)
    decimals = erc20.decimals()
    value_raw = int(value * (10 ** decimals))
    nonce = erc20.web3.eth.get_transaction_count(keystore["address"])
    tx = erc20.contract.functions.approve(spender, value_raw).build_transaction(
        {
            "from": keystore["address"],
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": erc20.web3.eth.gas_price,
        }
    )
    signed = erc20.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = erc20.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted tx hash: {tx_hash.hex()}")


@erc20_app.command()
def decimals(
    ctx: typer.Context, contract: str = typer.Option(..., help="ERC20 contract address")
):
    """Query ERC20 decimals"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    erc20 = load_erc20(contract, rpc)
    print(f"[green]Decimals: {erc20.decimals()}")


@erc20_app.command()
def symbol(
    ctx: typer.Context, contract: str = typer.Option(..., help="ERC20 contract address")
):
    """Query ERC20 symbol"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    erc20 = load_erc20(contract, rpc)
    print(f"[green]Symbol: {erc20.symbol()}")


@erc20_app.command()
def name(
    ctx: typer.Context, contract: str = typer.Option(..., help="ERC20 contract address")
):
    """Query ERC20 name"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    erc20 = load_erc20(contract, rpc)
    print(f"[green]Name: {erc20.name()}")
