import typer
from rich import print
from web3 import Web3
import json
import os
from hetu_pycli.src.hetu.wrapper.subnet_amm import SubnetAMM
from eth_account import Account
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path
import getpass

AMM_ABI_PATH = os.path.join(
    os.path.dirname(__file__), "../../../contracts/SubnetAMM.abi"
)

amm_app = typer.Typer(help="Subnet AMM contract operations")

def load_amm(contract: str, rpc: str):
    abi_path = os.path.abspath(AMM_ABI_PATH)
    if not os.path.exists(abi_path):
        print(f"[red]ABI file not found: {abi_path}")
        raise typer.Exit(1)
    with open(abi_path, "r") as f:
        abi = json.load(f)
    provider = Web3.HTTPProvider(rpc)
    return SubnetAMM(contract, provider, abi)

def get_contract_address(ctx, cli_contract_key: str, param_contract: str):
    config = ctx.obj or {}
    contract_addr = param_contract or config.get(cli_contract_key)
    if not contract_addr:
        print(f"[red]No contract address provided or found in config for {cli_contract_key}.")
        raise typer.Exit(1)
    print(f"[yellow]Using contract address: {contract_addr}")
    return contract_addr

@amm_app.command()
def alpha_price(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
):
    """Query current alpha price"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    amm = load_amm(contract, rpc)
    print(f"[green]Alpha Price: {amm.getAlphaPrice()}")

@amm_app.command()
def pool_info(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
):
    """Query pool info"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    amm = load_amm(contract, rpc)
    print(f"[green]Pool Info: {amm.getPoolInfo()}")

@amm_app.command()
def statistics(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
):
    """Query pool statistics"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    amm = load_amm(contract, rpc)
    print(f"[green]Statistics: {amm.getStatistics()}")

@amm_app.command()
def swap_preview(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    amount_in: float = typer.Option(..., help="Input amount (in HETU or ALPHA)"),
    is_hetu_to_alpha: bool = typer.Option(..., help="True for HETU->ALPHA, False for ALPHA->HETU"),
):
    """Preview swap result and price impact"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    amm = load_amm(contract, rpc)
    amount_in_wei = amm.web3.to_wei(amount_in, "ether")
    print(f"[green]Swap Preview: {amm.getSwapPreview(amount_in_wei, is_hetu_to_alpha)}")

@amm_app.command()
def sim_swap_alpha_for_hetu(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    alpha_amount: float = typer.Option(..., help="Alpha amount (in ALPHA)"),
):
    """Simulate swap ALPHA for HETU"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    amm = load_amm(contract, rpc)
    alpha_amount_wei = amm.web3.to_wei(alpha_amount, "ether")
    print(f"[green]Simulated HETU Out: {amm.simSwapAlphaForHETU(alpha_amount_wei)}")

@amm_app.command()
def sim_swap_hetu_for_alpha(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    hetu_amount: float = typer.Option(..., help="HETU amount (in HETU)"),
):
    """Simulate swap HETU for ALPHA"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    amm = load_amm(contract, rpc)
    hetu_amount_wei = amm.web3.to_wei(hetu_amount, "ether")
    print(f"[green]Simulated ALPHA Out: {amm.simSwapHETUForAlpha(hetu_amount_wei)}")

@amm_app.command()
def inject_liquidity(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    hetu_amount: float = typer.Option(..., help="HETU amount to add (in HETU)"),
    alpha_amount: float = typer.Option(..., help="ALPHA amount to add (in ALPHA)"),
):
    """Inject liquidity into the pool"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm_address", contract)
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
    amm = load_amm(contract, rpc)
    from_address = keystore["address"]
    nonce = amm.web3.eth.get_transaction_count(from_address)
    hetu_amount_wei = amm.web3.to_wei(hetu_amount, "ether")
    alpha_amount_wei = amm.web3.to_wei(alpha_amount, "ether")
    tx = amm.contract.functions.injectLiquidity(hetu_amount_wei, alpha_amount_wei).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": amm.web3.eth.gas_price,
        }
    )
    signed = amm.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = amm.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted inject liquidity tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = amm.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Inject liquidity succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Inject liquidity failed in block {receipt.blockNumber}")

@amm_app.command()
def withdraw_liquidity(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    hetu_amount: float = typer.Option(..., help="HETU amount to withdraw (in HETU)"),
    alpha_amount: float = typer.Option(..., help="ALPHA amount to withdraw (in ALPHA)"),
    to: str = typer.Option(..., help="Recipient address"),
):
    """Withdraw liquidity from the pool"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm", contract)
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
    amm = load_amm(contract, rpc)
    from_address = keystore["address"]
    nonce = amm.web3.eth.get_transaction_count(from_address)
    hetu_amount_wei = amm.web3.to_wei(hetu_amount, "ether")
    alpha_amount_wei = amm.web3.to_wei(alpha_amount, "ether")
    tx = amm.contract.functions.withdrawLiquidity(hetu_amount_wei, alpha_amount_wei, to).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": amm.web3.eth.gas_price,
        }
    )
    signed = amm.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = amm.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted withdraw liquidity tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = amm.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Withdraw liquidity succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Withdraw liquidity failed in block {receipt.blockNumber}")

@amm_app.command()
def swap_alpha_for_hetu(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    alpha_amount_in: float = typer.Option(..., help="Alpha amount in (in ALPHA)"),
    hetu_amount_out_min: float = typer.Option(..., help="Minimum HETU out (in HETU)"),
    to: str = typer.Option(..., help="Recipient address"),
):
    """Swap ALPHA for HETU"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm", contract)
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
    amm = load_amm(contract, rpc)
    from_address = keystore["address"]
    nonce = amm.web3.eth.get_transaction_count(from_address)
    alpha_amount_in_wei = amm.web3.to_wei(alpha_amount_in, "ether")
    hetu_amount_out_min_wei = amm.web3.to_wei(hetu_amount_out_min, "ether")
    tx = amm.contract.functions.swapAlphaForHETU(alpha_amount_in_wei, hetu_amount_out_min_wei, to).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": amm.web3.eth.gas_price,
        }
    )
    signed = amm.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = amm.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted swap ALPHA for HETU tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = amm.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Swap ALPHA for HETU succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Swap ALPHA for HETU failed in block {receipt.blockNumber}")

@amm_app.command()
def swap_hetu_for_alpha(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    hetu_amount_in: float = typer.Option(..., help="HETU amount in (in HETU)"),
    alpha_amount_out_min: float = typer.Option(..., help="Minimum ALPHA out (in ALPHA)"),
    to: str = typer.Option(..., help="Recipient address"),
):
    """Swap HETU for ALPHA"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "amm", contract)
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
    amm = load_amm(contract, rpc)
    from_address = keystore["address"]
    nonce = amm.web3.eth.get_transaction_count(from_address)
    hetu_amount_in_wei = amm.web3.to_wei(hetu_amount_in, "ether")
    alpha_amount_out_min_wei = amm.web3.to_wei(alpha_amount_out_min, "ether")
    tx = amm.contract.functions.swapHETUForAlpha(hetu_amount_in_wei, alpha_amount_out_min_wei, to).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": amm.web3.eth.gas_price,
        }
    )
    signed = amm.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = amm.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted swap HETU for ALPHA tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = amm.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Swap HETU for ALPHA succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Swap HETU for ALPHA failed in block {receipt.blockNumber}") 