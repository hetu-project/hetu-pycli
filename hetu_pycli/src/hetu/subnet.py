import typer
from rich import print
from web3 import Web3
import json
import os
from hetu_pycli.src.hetu.erc20 import load_erc20
from hetu_pycli.src.hetu.wrapper.subnet_mgr import SubnetMgr
from eth_account import Account
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path
import getpass

SUBNET_ABI_PATH = os.path.join(
    os.path.dirname(__file__), "../../../contracts/SubnetManager.abi"
)

subnet_app = typer.Typer(help="Subnet manager contract operations")

def load_subnet_mgr(contract: str, rpc: str):
    abi_path = os.path.abspath(SUBNET_ABI_PATH)
    if not os.path.exists(abi_path):
        print(f"[red]ABI file not found: {abi_path}")
        raise typer.Exit(1)
    with open(abi_path, "r") as f:
        abi = json.load(f)
    provider = Web3.HTTPProvider(rpc)
    return SubnetMgr(contract, provider, abi)

def get_contract_address(ctx, cli_contract_key: str, param_contract: str):
    config = ctx.obj or {}
    contract_addr = param_contract or config.get(cli_contract_key)
    if not contract_addr:
        print(f"[red]No contract address provided or found in config for {cli_contract_key}.")
        raise typer.Exit(1)
    print(f"[yellow]Using contract address: {contract_addr}")
    return contract_addr

@subnet_app.command()
def next_netuid(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
):
    """Query next netuid"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]Next netuid: {subnet_mgr.getNextNetuid()}")

@subnet_app.command()
def subnet_details(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query subnet details by netuid"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]Subnet Details: {subnet_mgr.getSubnetDetails(netuid)}")

@subnet_app.command()
def subnet_info(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query subnet info by netuid"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    subnet_info = subnet_mgr.getSubnetInfo(netuid)
    print(f"[green]Subnet Info\n- Netuid: {subnet_info[0]}\n- Owner: {subnet_info[1]}\n- Alpha Token: {subnet_info[2]}\n- AMM Pool: {subnet_info[3]}\n- Locked Amount: {subnet_info[4]}\n- Pool Initial Tao: {subnet_info[5]}\n- Burned Amount: {subnet_info[6]}\n- Created At: {subnet_info[7]}\n- Is Active: {subnet_info[8]}\n- Name: {subnet_info[9]}\n- Description: {subnet_info[10]}")

@subnet_app.command()
def subnet_params(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query subnet params by netuid"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]Subnet Params: {subnet_mgr.getSubnetParams(netuid)}")

@subnet_app.command()
def user_subnets(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    user: str = typer.Option(..., help="User address to query"),
):
    """Query all subnets for a user"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]User Subnets: {subnet_mgr.getUserSubnets(user)}")

@subnet_app.command()
def total_networks(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
):
    """Query total number of networks"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]Total Networks: {subnet_mgr.totalNetworks()}")

@subnet_app.command(
    name="regist"
)
def register_network(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    name: str = typer.Option(..., help="Network name"),
    description: str = typer.Option(..., help="Network description"),
    token_name: str = typer.Option(..., help="Token name"),
    token_symbol: str = typer.Option(..., help="Token symbol"),
):
    """Register a new network"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
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
    subnet_mgr = load_subnet_mgr(contract, rpc)
    from_address = keystore["address"]
    nonce = subnet_mgr.web3.eth.get_transaction_count(from_address)
    tx = subnet_mgr.contract.functions.registerNetwork(name, description, token_name, token_symbol).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 5000000,
            "gasPrice": subnet_mgr.web3.eth.gas_price,
        }
    )
    signed = subnet_mgr.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = subnet_mgr.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted register network tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = subnet_mgr.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Register network succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Register network failed in block {receipt.blockNumber}, receipt {receipt}")

@subnet_app.command()
def update_subnet_info(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    new_name: str = typer.Option(..., help="New subnet name"),
    new_description: str = typer.Option(..., help="New subnet description"),
):
    """Update subnet info (name/description)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
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
    subnet_mgr = load_subnet_mgr(contract, rpc)
    from_address = keystore["address"]
    nonce = subnet_mgr.web3.eth.get_transaction_count(from_address)
    tx = subnet_mgr.contract.functions.updateSubnetInfo(netuid, new_name, new_description).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": subnet_mgr.web3.eth.gas_price,
        }
    )
    signed = subnet_mgr.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = subnet_mgr.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted update subnet info tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = subnet_mgr.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Update subnet info succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Update subnet info failed in block {receipt.blockNumber}")

@subnet_app.command()
def activate_subnet(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid to activate"),
):
    """Activate a subnet (write tx)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
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
    subnet_mgr = load_subnet_mgr(contract, rpc)
    from_address = keystore["address"]
    nonce = subnet_mgr.web3.eth.get_transaction_count(from_address)
    tx = subnet_mgr.contract.functions.activateSubnet(netuid).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": subnet_mgr.web3.eth.gas_price,
        }
    )
    signed = subnet_mgr.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = subnet_mgr.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted activate subnet tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = subnet_mgr.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Activate subnet succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Activate subnet failed in block {receipt.blockNumber}")


@subnet_app.command()
def update_network_params(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    network_min_lock: int = typer.Option(..., help="New networkMinLock (uint256)"),
    network_rate_limit: int = typer.Option(..., help="New networkRateLimit (uint256)"),
    lock_reduction_interval: int = typer.Option(..., help="New lockReductionInterval (uint256)"),
):
    """Update network-level parameters (write tx)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
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
    subnet_mgr = load_subnet_mgr(contract, rpc)
    from_address = keystore["address"]
    nonce = subnet_mgr.web3.eth.get_transaction_count(from_address)
    tx = subnet_mgr.contract.functions.updateNetworkParams(
        network_min_lock, network_rate_limit, lock_reduction_interval
    ).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": subnet_mgr.web3.eth.gas_price,
        }
    )
    signed = subnet_mgr.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = subnet_mgr.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted update network params tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = subnet_mgr.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Update network params succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Update network params failed in block {receipt.blockNumber}, receipt {receipt}")

@subnet_app.command()
def update_subnet_params(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid to update"),
    new_hyperparams: str = typer.Option(..., help="New hyperparams as JSON string or file path"),
):
    """Update subnet hyperparams (write tx)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
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
    # Parse new_hyperparams as JSON string or file
    import json as _json
    if os.path.isfile(new_hyperparams):
        with open(new_hyperparams, 'r') as f:
            hyperparams = _json.load(f)
    else:
        hyperparams = _json.loads(new_hyperparams)
    # Convert dict to tuple if needed (assume order matches contract)
    if isinstance(hyperparams, dict):
        hyperparams = tuple(hyperparams.values())
    elif isinstance(hyperparams, list):
        hyperparams = tuple(hyperparams)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    from_address = keystore["address"]
    nonce = subnet_mgr.web3.eth.get_transaction_count(from_address)
    tx = subnet_mgr.contract.functions.updateSubnetHyperparams(netuid, hyperparams).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": subnet_mgr.web3.eth.gas_price,
        }
    )
    signed = subnet_mgr.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = subnet_mgr.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted update subnet hyperparams tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = subnet_mgr.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Update subnet hyperparams succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Update subnet hyperparams failed in block {receipt.blockNumber}, receipt {receipt}")

@subnet_app.command()
def get_network_lock_cost(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
):
    """Query network lock cost"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    balance = subnet_mgr.getNetworkLockCost()
    whetu = subnet_mgr.hetuToken()
    erc20 = load_erc20(whetu, rpc)
    decimals = erc20.decimals()
    value = balance / (10 ** decimals)
    value_str = f"{value:,.{decimals}f}".rstrip('0').rstrip('.')
    print(f"[green]Network lock cost: {value_str} (raw: {balance}, decimals: {decimals})")

@subnet_app.command()
def get_subnet_hyperparams(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query subnet hyperparams by netuid"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]Subnet Hyperparams: {subnet_mgr.getSubnetHyperparams(netuid)}")

@subnet_app.command()
def hetu_token(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
):
    """Query hetuToken address"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]hetuToken: {subnet_mgr.hetuToken()}")

@subnet_app.command()
def network_last_lock(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
):
    """Query networkLastLock"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]networkLastLock: {subnet_mgr.networkLastLock()}")

@subnet_app.command()
def network_last_lock_block(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
):
    """Query networkLastLockBlock"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]networkLastLockBlock: {subnet_mgr.networkLastLockBlock()}")

@subnet_app.command()
def owner_subnets(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    owner: str = typer.Option(..., help="Owner address"),
    idx: int = typer.Option(..., help="Index (uint256)"),
):
    """Query ownerSubnets(owner, idx)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]ownerSubnets: {subnet_mgr.ownerSubnets(owner, idx)}")

@subnet_app.command()
def subnet_exists(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query subnetExists(netuid)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]subnetExists: {subnet_mgr.subnetExists(netuid)}")

@subnet_app.command()
def subnet_hyperparams(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query subnetHyperparams(netuid)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]subnetHyperparams: {subnet_mgr.subnetHyperparams(netuid)}")

@subnet_app.command()
def subnets(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Subnet manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query subnets(netuid)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "subnet_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    subnet_mgr = load_subnet_mgr(contract, rpc)
    print(f"[green]subnets: {subnet_mgr.subnets(netuid)}") 