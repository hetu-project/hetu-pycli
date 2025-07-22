import typer
from rich import print
from web3 import Web3
import json
import os
from hetu_pycli.src.hetu.erc20 import load_erc20
from hetu_pycli.src.hetu.wrapper.global_staking import GlobalStaking
from eth_account import Account
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path
import getpass

STAKING_ABI_PATH = os.path.join(
    os.path.dirname(__file__), "../../../contracts/GlobalStaking.abi"
)

staking_app = typer.Typer(help="Global staking contract operations")

def load_staking(contract: str, rpc: str):
    abi_path = os.path.abspath(STAKING_ABI_PATH)
    if not os.path.exists(abi_path):
        print(f"[red]ABI file not found: {abi_path}")
        raise typer.Exit(1)
    with open(abi_path, "r") as f:
        abi = json.load(f)
    provider = Web3.HTTPProvider(rpc)
    return GlobalStaking(contract, provider, abi)

def get_contract_address(ctx, cli_contract_key: str, param_contract: str):
    config = ctx.obj or {}
    contract_addr = param_contract or config.get(cli_contract_key)
    if not contract_addr:
        print(f"[red]No contract address provided or found in config for {cli_contract_key}.")
        raise typer.Exit(1)
    print(f"[yellow]Using contract address: {contract_addr}")
    return contract_addr

@staking_app.command()
def total_staked(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
):
    """Query total staked HETU"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "staking_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    staking = load_staking(contract, rpc)
    all_staking = staking.getTotalStaked()
    whetu = staking.hetuToken()
    erc20 = load_erc20(whetu, rpc)
    decimals = erc20.decimals()
    value = all_staking / (10 ** decimals)
    value_str = f"{value:,.{decimals}f}".rstrip('0').rstrip('.')
    print(f"[green]Total Staked: {value_str} (raw: {all_staking}, decimals: {decimals})")

@staking_app.command()
def stake_info(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
    user: str = typer.Option(..., help="User address to query"),
):
    """Query stake info for a user"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    contract = get_contract_address(ctx, "staking_address", contract)
    staking = load_staking(contract, rpc)
    print(f"[green]Stake Info: {staking.getStakeInfo(user)}")

@staking_app.command()
def add_stake(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    amount: float = typer.Option(..., help="Amount to stake (in HETU)"),
):
    """Add global stake (stake HETU)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "staking_address", contract)
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
    staking = load_staking(contract, rpc)
    from_address = keystore["address"]
    nonce = staking.web3.eth.get_transaction_count(from_address)
    amount_wei = staking.web3.to_wei(amount, "ether")
    tx = staking.contract.functions.addGlobalStake(amount_wei).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": staking.web3.eth.gas_price,
        }
    )
    signed = staking.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = staking.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted add stake tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = staking.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Add stake succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Add stake failed in block {receipt.blockNumber}")

@staking_app.command()
def remove_stake(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    amount: float = typer.Option(..., help="Amount to unstake (in HETU)"),
):
    """Remove global stake (unstake HETU)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    contract = get_contract_address(ctx, "staking_address", contract)
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
    staking = load_staking(contract, rpc)
    from_address = keystore["address"]
    nonce = staking.web3.eth.get_transaction_count(from_address)
    amount_wei = staking.web3.to_wei(amount, "ether")
    tx = staking.contract.functions.removeGlobalStake(amount_wei).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 500000,
            "gasPrice": staking.web3.eth.gas_price,
        }
    )
    signed = staking.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = staking.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted remove stake tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = staking.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Remove stake succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Remove stake failed in block {receipt.blockNumber}")

@staking_app.command()
def claim_rewards(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
):
    """Claim staking rewards"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    contract = get_contract_address(ctx, "staking_address", contract)
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
    staking = load_staking(contract, rpc)
    from_address = keystore["address"]
    nonce = staking.web3.eth.get_transaction_count(from_address)
    tx = staking.contract.functions.claimRewards().build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 150000,
            "gasPrice": staking.web3.eth.gas_price,
        }
    )
    signed = staking.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = staking.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted claim rewards tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = staking.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Claim rewards succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Claim rewards failed in block {receipt.blockNumber}")

@staking_app.command()
def available_stake(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
    user: str = typer.Option(..., help="User address to query"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query available stake for a user in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    contract = get_contract_address(ctx, "staking_address", contract)
    staking = load_staking(contract, rpc)
    print(f"[green]Available Stake: {staking.getAvailableStake(user, netuid)}")

@staking_app.command()
def effective_stake(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
    user: str = typer.Option(..., help="User address to query"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query effective stake for a user in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    contract = get_contract_address(ctx, "staking_address", contract)
    staking = load_staking(contract, rpc)
    print(f"[green]Effective Stake: {staking.getEffectiveStake(user, netuid)}")

@staking_app.command()
def locked_stake(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
    user: str = typer.Option(..., help="User address to query"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query locked stake for a user in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    contract = get_contract_address(ctx, "staking_address", contract)
    staking = load_staking(contract, rpc)
    print(f"[green]Locked Stake: {staking.getLockedStake(user, netuid)}")

@staking_app.command()
def allocate_to_subnet(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    amount: float = typer.Option(..., help="Amount to allocate (in HETU)"),
):
    """Allocate stake to a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    contract = get_contract_address(ctx, "staking_address", contract)
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
    staking = load_staking(contract, rpc)
    from_address = keystore["address"]
    nonce = staking.web3.eth.get_transaction_count(from_address)
    amount_wei = staking.web3.to_wei(amount, "ether")
    tx = staking.contract.functions.allocateToSubnet(netuid, amount_wei).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 500000,
            "gasPrice": staking.web3.eth.gas_price,
        }
    )
    signed = staking.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = staking.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted allocate to subnet tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = staking.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Allocate to subnet succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Allocate to subnet failed in block {receipt.blockNumber}")

@staking_app.command()
def subnet_allocation(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Staking contract address"),
    user: str = typer.Option(..., help="User address to query"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query subnet allocation for a user"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    contract = get_contract_address(ctx, "staking_address", contract)
    staking = load_staking(contract, rpc)
    print(f"[green]Subnet Allocation: {staking.getSubnetAllocation(user, netuid)}") 