import typer
from rich import print
from web3 import Web3
import json
import os
from hetu_pycli.src.hetu.wrapper.whetu import Whetu
from eth_account import Account
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path
import getpass

WHETU_ABI_PATH = os.path.join(
    os.path.dirname(__file__), "../../../contracts/WHETU.abi"
)

whetu_app = typer.Typer(help="WHETU contract operations")

def load_whetu(contract: str, rpc: str):
    abi_path = os.path.abspath(WHETU_ABI_PATH)
    if not os.path.exists(abi_path):
        print(f"[red]ABI file not found: {abi_path}")
        raise typer.Exit(1)
    with open(abi_path, "r") as f:
        abi = json.load(f)
    provider = Web3.HTTPProvider(rpc)
    return Whetu(contract, provider, abi)

def get_contract_address(ctx, cli_contract_key: str, param_contract: str):
    config = ctx.obj or {}
    contract_addr = param_contract or config.get(cli_contract_key)
    if not contract_addr:
        print(f"[red]No contract address provided or found in config for {cli_contract_key}.")
        raise typer.Exit(1)
    print(f"[yellow]Using contract address: {contract_addr}")
    return contract_addr

@whetu_app.command()
def domain_separator(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
):
    """Query DOMAIN_SEPARATOR of the contract"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    whetu = load_whetu(contract, rpc)
    print(f"[green]DOMAIN_SEPARATOR: {whetu.DOMAIN_SEPARATOR()}")

@whetu_app.command()
def total_eth(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
):
    """Query totalHETU of the contract"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    whetu = load_whetu(contract, rpc)
    print(f"[green]totalHETU: {whetu.totalETH()}")

@whetu_app.command()
def total_supply(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
):
    """Query totalSupply of the contract"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    whetu = load_whetu(contract, rpc)
    print(f"[green]totalSupply: {whetu.totalSupply()}")

@whetu_app.command()
def deposit(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    value: float = typer.Option(..., help="HETU amount to deposit (in ahetu)"),
):
    """Deposit HETU into the contract (sign and broadcast using local keystore)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
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
    whetu = load_whetu(contract, rpc)
    from_address = keystore["address"]
    nonce = whetu.web3.eth.get_transaction_count(from_address)
    value_wei = whetu.web3.to_wei(value, "ether")
    tx = whetu.contract.functions.deposit().build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "value": value_wei,
            "gas": 150000,
            "gasPrice": whetu.web3.eth.gas_price,
        }
    )
    signed = whetu.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = whetu.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted deposit tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = whetu.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Deposit succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Deposit failed in block {receipt.blockNumber}")

@whetu_app.command()
def withdraw(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    amount: float = typer.Option(..., help="Amount to withdraw (in ether)"),
):
    """Withdraw HETU from the contract (sign and broadcast using local keystore)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
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
    whetu = load_whetu(contract, rpc)
    from_address = keystore["address"]
    nonce = whetu.web3.eth.get_transaction_count(from_address)
    amount_wei = whetu.web3.to_wei(amount, "ether")
    tx = whetu.contract.functions.withdraw(amount_wei).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 150000,
            "gasPrice": whetu.web3.eth.gas_price,
        }
    )
    signed = whetu.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = whetu.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted withdraw tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = whetu.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Withdraw succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Withdraw failed in block {receipt.blockNumber}")

@whetu_app.command()
def nonces(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
    owner: str = typer.Option(..., help="Owner address to query nonce for"),
):
    """Query nonce for an owner (for permit)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    whetu = load_whetu(contract, rpc)
    print(f"[green]Nonce for {owner}: {whetu.nonces(owner)}")

@whetu_app.command()
def eip712_domain(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
):
    """Query EIP712 domain info"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    whetu = load_whetu(contract, rpc)
    print(f"[green]EIP712 Domain: {whetu.eip712Domain()}")

@whetu_app.command()
def balance_of(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
    name: str = typer.Argument(..., help="Wallet name or address to query"),
):
    """Query WHETU token balance of an account"""
    config = ctx.obj
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
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
    whetu = load_whetu(contract, rpc)
    balance = whetu.balanceOf(address)
    decimals = whetu.decimals()
    value = balance / (10 ** decimals)
    value_str = f"{value:,.{decimals}f}".rstrip('0').rstrip('.')
    print(f"[green]Balance: {value_str} (raw: {balance}, decimals: {decimals})")

@whetu_app.command()
def transfer(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
    to: str = typer.Option(..., help="Recipient address"),
    value: float = typer.Option(..., help="Amount to transfer (human readable, e.g. 1.23)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
):
    """Transfer WHETU tokens, sign and broadcast using local keystore (by wallet name or address)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
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
    whetu = load_whetu(contract, rpc)
    decimals = whetu.decimals()
    value_raw = int(value * (10 ** decimals))
    nonce = whetu.web3.eth.get_transaction_count(keystore["address"])
    tx = whetu.contract.functions.transfer(to, value_raw).build_transaction(
        {
            "from": keystore["address"],
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": whetu.web3.eth.gas_price,
        }
    )
    signed = whetu.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = whetu.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted transfer tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = whetu.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Transfer succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Transfer failed in block {receipt.blockNumber}")

@whetu_app.command()
def approve(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
    spender: str = typer.Option(..., help="Spender address"),
    value: float = typer.Option(..., help="Amount to approve (human readable, e.g. 1.23)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
):
    """Approve WHETU allowance, sign and broadcast using local keystore (by wallet name or address)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
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
    whetu = load_whetu(contract, rpc)
    decimals = whetu.decimals()
    value_raw = int(value * (10 ** decimals))
    print(f"value_raw: {value_raw}")
    nonce = whetu.web3.eth.get_transaction_count(keystore["address"])
    tx = whetu.contract.functions.approve(spender, value_raw).build_transaction(
        {
            "from": keystore["address"],
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": whetu.web3.eth.gas_price,
        }
    )
    signed = whetu.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = whetu.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted approve tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = whetu.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Approve succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Approve failed in block {receipt.blockNumber}")

@whetu_app.command()
def decimals(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
):
    """Query WHETU decimals"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    whetu = load_whetu(contract, rpc)
    print(f"[green]Decimals: {whetu.decimals()}")

@whetu_app.command()
def symbol(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
):
    """Query WHETU symbol"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    whetu = load_whetu(contract, rpc)
    print(f"[green]Symbol: {whetu.symbol()}")

@whetu_app.command()
def name(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="WHETU contract address"),
):
    """Query WHETU name"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "whetu_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    whetu = load_whetu(contract, rpc)
    print(f"[green]Name: {whetu.name()}") 