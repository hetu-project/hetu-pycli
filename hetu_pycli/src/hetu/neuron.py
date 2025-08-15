import typer
from rich import print
from web3 import Web3
import json
import os
from hetu_pycli.src.hetu.wrapper.neuron_mgr import NeuronMgr
from eth_account import Account
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path
import getpass

NEURON_ABI_PATH = os.path.join(
    os.path.dirname(__file__), "../../../contracts/NeuronManager.abi"
)

neuron_app = typer.Typer(help="Neuron manager contract operations")

def get_contract_address(ctx, cli_contract_key: str, param_contract: str):
    config = ctx.obj or {}
    contract_addr = param_contract or config.get(cli_contract_key)
    if not contract_addr:
        print(f"[red]No contract address provided or found in config for {cli_contract_key}.")
        raise typer.Exit(1)
    print(f"[yellow]Using contract address: {contract_addr}")
    return contract_addr

def load_neuron_mgr(contract: str, rpc: str):
    abi_path = os.path.abspath(NEURON_ABI_PATH)
    if not os.path.exists(abi_path):
        print(f"[red]ABI file not found: {abi_path}")
        raise typer.Exit(1)
    with open(abi_path, "r") as f:
        abi = json.load(f)
    provider = Web3.HTTPProvider(rpc)
    return NeuronMgr(contract, provider, abi)

@neuron_app.command()
def get_neuron_info(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    account: str = typer.Option(..., help="Neuron account address or wallet name"),
):
    """Query neuron info by netuid and account"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    # 检查是否是钱包名称并转换为地址
    address = account
    config = ctx.obj
    wallet_path = get_wallet_path(config)
    if not (address.startswith('0x') and len(address) == 42):
        try:
            keystore = load_keystore(account, wallet_path)
            address = keystore.get("address")
            print(f"[yellow]Converted wallet name '{account}' to address: {address}")
        except Exception:
            print(f"[red]Wallet not found: {account}")
            raise typer.Exit(1)
        account = address
    
    mgr = load_neuron_mgr(contract, rpc)
    print(f"[green]Neuron Info: {mgr.getNeuronInfo(netuid, account)}")

@neuron_app.command()
def get_subnet_neuron_count(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query neuron count in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_neuron_mgr(contract, rpc)
    print(f"[green]Subnet Neuron Count: {mgr.getSubnetNeuronCount(netuid)}")

@neuron_app.command()
def get_subnet_neurons(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query all neuron addresses in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_neuron_mgr(contract, rpc)
    print(f"[green]Subnet Neurons: {mgr.getSubnetNeurons(netuid)}")

@neuron_app.command()
def get_subnet_validator_count(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query validator count in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_neuron_mgr(contract, rpc)
    print(f"[green]Subnet Validator Count: {mgr.getSubnetValidatorCount(netuid)}")

@neuron_app.command()
def get_subnet_validators(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query all validator addresses in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_neuron_mgr(contract, rpc)
    print(f"[green]Subnet Validators: {mgr.getSubnetValidators(netuid)}")

@neuron_app.command()
def is_neuron(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    account: str = typer.Option(..., help="Neuron account address or wallet name"),
):
    """Check if account is a neuron in subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    # 检查是否是钱包名称并转换为地址
    address = account
    config = ctx.obj
    wallet_path = get_wallet_path(config)
    if not (address.startswith('0x') and len(address) == 42):
        try:
            keystore = load_keystore(account, wallet_path)
            address = keystore.get("address")
            print(f"[yellow]Converted wallet name '{account}' to address: {address}")
        except Exception:
            print(f"[red]Wallet not found: {account}")
            raise typer.Exit(1)
        account = address
    
    mgr = load_neuron_mgr(contract, rpc)
    print(f"[green]Is Neuron: {mgr.isNeuron(netuid, account)}")

@neuron_app.command()
def is_validator(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    account: str = typer.Option(..., help="Neuron account address or wallet name"),
):
    """Check if account is a validator in subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    # 检查是否是钱包名称并转换为地址
    address = account
    config = ctx.obj
    wallet_path = get_wallet_path(config)
    if not (address.startswith('0x') and len(address) == 42):
        try:
            keystore = load_keystore(account, wallet_path)
            address = keystore.get("address")
            print(f"[yellow]Converted wallet name '{account}' to address: {address}")
        except Exception:
            print(f"[red]Wallet not found: {account}")
            raise typer.Exit(1)
        account = address
    
    mgr = load_neuron_mgr(contract, rpc)
    print(f"[green]Is Validator: {mgr.isValidator(netuid, account)}")

@neuron_app.command()
def neuron_list(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    idx: int = typer.Option(..., help="Index (uint256)"),
):
    """Query neuronList(netuid, idx)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_neuron_mgr(contract, rpc)
    print(f"[green]neuronList: {mgr.neuronList(netuid, idx)}")

@neuron_app.command()
def neurons(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    account: str = typer.Option(..., help="Neuron account address"),
):
    """Query neurons(netuid, account)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_neuron_mgr(contract, rpc)
    print(f"[green]neurons: {mgr.neurons(netuid, account)}")

@neuron_app.command()
def can_register_neuron(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    user: str = typer.Option(..., help="User address to check"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    is_validator_role: bool = typer.Option(False, "--is-validator-role/--no-validator-role", help="Is validator role"),
):
    """Check if a user can register as a neuron"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_neuron_mgr(contract, rpc)
    
    # 由于 ABI 中没有 canRegisterNeuron 函数，我们显示基本信息
    print(f"[yellow]Checking registration eligibility for user {user} on subnet {netuid}")
    print(f"[yellow]Validator role: {is_validator_role}")
    print(f"[yellow]Note: canRegisterNeuron function not available in current ABI")
    print(f"[yellow]Please check subnet status and user stake allocation manually")

@neuron_app.command(
    name="regist"
)
def register_neuron(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    is_validator_role: bool = typer.Option(False, "--is-validator-role/--no-validator-role", help="Is validator role?"),
    axon_endpoint: str = typer.Option(..., help="Axon endpoint"),
    axon_port: int = typer.Option(..., help="Axon port (uint32)"),
    prometheus_endpoint: str = typer.Option(..., help="Prometheus endpoint"),
    prometheus_port: int = typer.Option(..., help="Prometheus port (uint32)"),
    stake_amount: float = typer.Option(100.0, help="Stake amount in HETU (default: 100)"),
):
    """Register a neuron (write tx)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
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
    mgr = load_neuron_mgr(contract, rpc)
    from_address = keystore["address"]
    nonce = mgr.web3.eth.get_transaction_count(from_address)
    
    # 转换质押金额为 wei
    stake_amount_wei = mgr.web3.to_wei(stake_amount, "ether")
    print(f"[yellow]Using stake amount: {stake_amount} HETU ({stake_amount_wei} wei)")
    
    tx = mgr.contract.functions.registerNeuronWithStakeAllocation(
        netuid, stake_amount_wei, is_validator_role, axon_endpoint, axon_port, prometheus_endpoint, prometheus_port
    ).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 500000,
            "gasPrice": mgr.web3.eth.gas_price,
        }
    )
    signed = mgr.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = mgr.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted register neuron tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = mgr.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Register neuron succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Register neuron failed in block {receipt.blockNumber}, receipt {receipt}")

@neuron_app.command()
def deregister_neuron(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Neuron manager contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid to deregister from"),
):
    """Deregister a neuron (write tx)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "neuron_address", contract)
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
    mgr = load_neuron_mgr(contract, rpc)
    from_address = keystore["address"]
    nonce = mgr.web3.eth.get_transaction_count(from_address)
    tx = mgr.contract.functions.deregisterNeuron(netuid).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": mgr.web3.eth.gas_price,
        }
    )
    signed = mgr.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = mgr.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted deregister neuron tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = mgr.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Deregister neuron succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Deregister neuron failed in block {receipt.blockNumber}, receipt {receipt}") 