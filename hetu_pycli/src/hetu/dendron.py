import typer
from rich import print
from web3 import Web3
import json
import os
from hetu_pycli.src.hetu.wrapper.dendron_mgr import DendronMgr
from eth_account import Account
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path
import getpass

DENDRON_ABI_PATH = os.path.join(
    os.path.dirname(__file__), "../../../contracts/DendronManager.abi"
)

dendron_app = typer.Typer(help="Dendron manager contract operations")

def get_contract_address(ctx, cli_contract_key: str, param_contract: str):
    config = ctx.obj or {}
    contract_addr = param_contract or config.get(cli_contract_key)
    if not contract_addr:
        print(f"[red]No contract address provided or found in config for {cli_contract_key}.")
        raise typer.Exit(1)
    print(f"[yellow]Using contract address: {contract_addr}")
    return contract_addr

def load_dendron_mgr(contract: str, rpc: str):
    abi_path = os.path.abspath(DENDRON_ABI_PATH)
    if not os.path.exists(abi_path):
        print(f"[red]ABI file not found: {abi_path}")
        raise typer.Exit(1)
    with open(abi_path, "r") as f:
        abi = json.load(f)
    provider = Web3.HTTPProvider(rpc)
    return DendronMgr(contract, provider, abi)

@dendron_app.command()
def get_dendron_info(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    account: str = typer.Option(..., help="Dendron account address or wallet name"),
):
    """Query dendron info by netuid and account"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
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
    
    mgr = load_dendron_mgr(contract, rpc)
    print(f"[green]Dendron Info: {mgr.getDendronInfo(netuid, account)}")

@dendron_app.command()
def get_subnet_dendron_count(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query dendron count in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_dendron_mgr(contract, rpc)
    print(f"[green]Subnet Dendron Count: {mgr.getSubnetDendronCount(netuid)}")

@dendron_app.command()
def get_subnet_dendrons(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query all dendron addresses in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_dendron_mgr(contract, rpc)
    print(f"[green]Subnet Dendrons: {mgr.getSubnetDendrons(netuid)}")

@dendron_app.command()
def get_subnet_validator_count(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query validator count in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_dendron_mgr(contract, rpc)
    print(f"[green]Subnet Validator Count: {mgr.getSubnetValidatorCount(netuid)}")

@dendron_app.command()
def get_subnet_validators(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
):
    """Query all validator addresses in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_dendron_mgr(contract, rpc)
    print(f"[green]Subnet Validators: {mgr.getSubnetValidators(netuid)}")

@dendron_app.command()
def is_dendron(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    account: str = typer.Option(..., help="Dendron account address or wallet name"),
):
    """Check if account is a dendron in subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
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
    
    mgr = load_dendron_mgr(contract, rpc)
    print(f"[green]Is Dendron: {mgr.isDendron(netuid, account)}")

@dendron_app.command()
def is_validator(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    account: str = typer.Option(..., help="Dendron account address or wallet name"),
):
    """Check if account is a validator in subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
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
    
    mgr = load_dendron_mgr(contract, rpc)
    print(f"[green]Is Validator: {mgr.isValidator(netuid, account)}")

@dendron_app.command()
def dendron_list(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    idx: int = typer.Option(..., help="Index (uint256)"),
):
    """Query dendronList(netuid, idx)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_dendron_mgr(contract, rpc)
    print(f"[green]dendronList: {mgr.dendronList(netuid, idx)}")

@dendron_app.command()
def dendrons(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    account: str = typer.Option(..., help="Dendron account address"),
):
    """Query dendrons(netuid, account)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_dendron_mgr(contract, rpc)
    print(f"[green]dendrons: {mgr.dendrons(netuid, account)}")

@dendron_app.command()
def can_register_dendron(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    user: str = typer.Option(..., help="User address to check"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    is_validator_role: bool = typer.Option(False, "--is-validator-role/--no-validator-role", help="Is validator role"),
):
    """Check if a user can register as a dendron"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    mgr = load_dendron_mgr(contract, rpc)
    
    # 由于 ABI 中没有 canRegisterDendron 函数，我们显示基本信息
    print(f"[yellow]Checking registration eligibility for user {user} on subnet {netuid}")
    print(f"[yellow]Validator role: {is_validator_role}")
    print(f"[yellow]Note: canRegisterDendron function not available in current ABI")
    print(f"[yellow]Please check subnet status and user stake allocation manually")

@dendron_app.command(
    name="regist"
)
def register_dendron(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    is_validator_role: bool = typer.Option(False, "--is-validator-role/--no-validator-role", help="Is validator role?"),
    axon_endpoint: str = typer.Option(..., help="Axon endpoint"),
    axon_port: int = typer.Option(..., help="Axon port (uint32)"),
    prometheus_endpoint: str = typer.Option(..., help="Prometheus endpoint"),
    prometheus_port: int = typer.Option(..., help="Prometheus port (uint32)"),
):
    """Register a dendron with automatic cost and stake requirement detection"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
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
    
    from_address = keystore["address"]
    
    # Load dendron manager
    mgr = load_dendron_mgr(contract, rpc)
    
    # Get subnet manager contract to query parameters
    from hetu_pycli.src.hetu.subnet import load_subnet_mgr, get_contract_address as get_subnet_contract
    subnet_contract = get_subnet_contract(ctx, "subnet_address", None)
    subnet_mgr = load_subnet_mgr(subnet_contract, rpc)
    
    # Get subnet parameters to determine required costs and thresholds
    print(f"[yellow]Querying subnet {netuid} parameters...")
    try:
        subnet_params = subnet_mgr.getSubnetParams(netuid)
        
        # Extract required parameters based on ABI structure
        # Note: These indices are based on the ABI structure shown in the wrapper
        base_burn_cost = subnet_params[10]  # baseBurnCost (might be baseDendronCost)
        validator_threshold = subnet_params[19]  # validatorThreshold
        dendron_threshold = subnet_params[20]  # dendronThreshold
        
        print(f"[green]Subnet {netuid} parameters:")
        print(f"[green]  - Base burn cost: {base_burn_cost} wei")
        print(f"[green]  - Validator threshold: {validator_threshold} wei")
        print(f"[green]  - Dendron threshold: {dendron_threshold} wei")
        
        # Determine required stake amount based on role
        if is_validator_role:
            required_stake_wei = validator_threshold
            print(f"[green]Required stake (validator): {mgr.web3.from_wei(required_stake_wei, 'ether')} HETU")
        else:
            required_stake_wei = dendron_threshold
            print(f"[green]Required stake (dendron): {mgr.web3.from_wei(required_stake_wei, 'ether')} HETU")
        
        # Total required = stake + registration cost
        total_required_wei = required_stake_wei + base_burn_cost
        total_required_hetu = mgr.web3.from_wei(total_required_wei, "ether")
        print(f"[green]Total required (stake + registration): {total_required_hetu} HETU")
        
    except Exception as e:
        print(f"[yellow]Warning: Could not get subnet parameters: {e}")
        print(f"[yellow]Using default values:")
        print(f"[yellow]  - Required stake: 100 HETU")
        print(f"[yellow]  - Registration cost: 10 HETU")
        print(f"[yellow]  - Total required: 110 HETU")
        required_stake_wei = mgr.web3.to_wei(100, "ether")
        base_burn_cost = mgr.web3.to_wei(10, "ether")
        total_required_wei = required_stake_wei + base_burn_cost
        total_required_hetu = 110.0
    
    # Check if user has sufficient global stake
    print(f"[yellow]Checking global stake allocation...")
    staking_contract = get_contract_address(ctx, "staking_address", None)
    from hetu_pycli.src.hetu.staking import load_staking
    staking = load_staking(staking_contract, rpc)
    
    # Use the correct getAvailableStake function which calculates: totalStaked - totalAllocated - totalCost
    available_stake = staking.getAvailableStake(from_address)
    available_stake_hetu = staking.web3.from_wei(available_stake, "ether")
    
    # Also get detailed stake info for display
    stake_info = staking.getStakeInfo(from_address)
    total_staked = stake_info[0]  # totalStaked
    total_allocated = stake_info[1]  # totalAllocated
    total_cost = stake_info[2]  # totalCost
    
    print(f"[green]Stake info for {from_address}:")
    print(f"[green]  - Total staked: {staking.web3.from_wei(total_staked, 'ether')} HETU")
    print(f"[green]  - Total allocated: {staking.web3.from_wei(total_allocated, 'ether')} HETU")
    print(f"[green]  - Total cost consumed: {staking.web3.from_wei(total_cost, 'ether')} HETU")
    print(f"[green]  - Available for allocation: {available_stake_hetu} HETU")
    
    if available_stake < total_required_wei:
        print(f"[red]Insufficient available stake!")
        print(f"[red]Required: {total_required_hetu} HETU")
        print(f"[red]Available: {available_stake_hetu} HETU")
        print(f"[yellow]Please add more global stake using: hetucli stake add-stake --sender {sender} --amount {total_required_hetu}")
        raise typer.Exit(1)
    
    print(f"[green]Available stake sufficient: {available_stake_hetu} HETU")
    
    # Load WHETU contract for allowance check
    from hetu_pycli.src.hetu.whetu import load_whetu
    whetu_contract = get_contract_address(ctx, "whetu_address", None)
    whetu = load_whetu(whetu_contract, rpc)
    
    # Check current allowance for staking contract
    print(f"[yellow]Checking WHETU allowance for staking...")
    current_allowance = whetu.allowance(from_address, staking_contract)
    decimals = whetu.decimals()
    
    if current_allowance < required_stake_wei:
        print(f"[yellow]Insufficient allowance. Approving {mgr.web3.from_wei(required_stake_wei, 'ether')} WHETU for staking...")
        nonce = whetu.web3.eth.get_transaction_count(from_address)
        approve_tx = whetu.contract.functions.approve(staking_contract, required_stake_wei).build_transaction(
            {
                "from": from_address,
                "nonce": nonce,
                "gas": 100000,
                "gasPrice": whetu.web3.eth.gas_price,
            }
        )
        signed_approve = whetu.web3.eth.account.sign_transaction(approve_tx, private_key)
        approve_tx_hash = whetu.web3.eth.send_raw_transaction(signed_approve.raw_transaction)
        print(f"[green]Broadcasted approve tx hash: {approve_tx_hash.hex()}")
        print("[yellow]Waiting for approve transaction receipt...")
        approve_receipt = whetu.web3.eth.wait_for_transaction_receipt(approve_tx_hash)
        if approve_receipt.status == 1:
            print(f"[green]Approve succeeded in block {approve_receipt.blockNumber}")
        else:
            print(f"[red]Approve failed in block {approve_receipt.blockNumber}")
            raise typer.Exit(1)
    else:
        print(f"[green]Sufficient allowance already exists: {current_allowance / (10 ** decimals)} WHETU")
    
    # Now register the dendron
    print(f"[yellow]Registering dendron with {mgr.web3.from_wei(required_stake_wei, 'ether')} HETU stake...")
    nonce = mgr.web3.eth.get_transaction_count(from_address)
    
    tx = mgr.contract.functions.registerNeuronWithStakeAllocation(
        netuid, required_stake_wei, is_validator_role, axon_endpoint, axon_port, prometheus_endpoint, prometheus_port
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
    print(f"[green]Broadcasted register dendron tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = mgr.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Register dendron succeeded in block {receipt.blockNumber}")
        print(f"[green]Dendron registered with {mgr.web3.from_wei(required_stake_wei, 'ether')} HETU stake")
        print(f"[green]Registration cost: {mgr.web3.from_wei(base_burn_cost, 'ether')} HETU")
        print(f"[green]Total cost: {total_required_hetu} HETU")
    else:
        print(f"[red]Register dendron failed in block {receipt.blockNumber}, receipt {receipt}")

@dendron_app.command()
def deregister_dendron(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    sender: str = typer.Option(None, help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid to deregister from"),
):
    """Deregister a dendron (write tx)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
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
    mgr = load_dendron_mgr(contract, rpc)
    from_address = keystore["address"]
    
    # Use the wrapper method instead of direct contract call
    try:
        # First check if the dendron exists and is active
        dendron_info = mgr.getDendronInfo(netuid, from_address)
        if not dendron_info[2]:  # isActive field
            print(f"[yellow]Dendron in subnet {netuid} is not active or doesn't exist")
            raise typer.Exit(1)
    except Exception as e:
        print(f"[red]Failed to get dendron info: {e}")
        raise typer.Exit(1)
    
    nonce = mgr.web3.eth.get_transaction_count(from_address)
    
    # Build transaction using the wrapper method
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
    print(f"[green]Broadcasted deregister dendron tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    receipt = mgr.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]Deregister dendron succeeded in block {receipt.blockNumber}")
    else:
        print(f"[red]Deregister dendron failed in block {receipt.blockNumber}, receipt {receipt}") 

@dendron_app.command()
def get_user_role(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Dendron manager contract address"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    user: str = typer.Option(..., help="User address or wallet name to check"),
):
    """Get user role in a subnet (validator, miner, or not registered)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "dendron_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    # 检查是否是钱包名称并转换为地址
    address = user
    config = ctx.obj
    wallet_path = get_wallet_path(config)
    if not (address.startswith('0x') and len(address) == 42):
        try:
            keystore = load_keystore(user, wallet_path)
            address = keystore.get("address")
            print(f"[yellow]Converted wallet name '{user}' to address: {address}")
        except Exception:
            print(f"[red]Wallet not found: {user}")
            raise typer.Exit(1)
        user = address
    
    mgr = load_dendron_mgr(contract, rpc)
    
    try:
        # 检查用户是否在子网中注册
        dendron_info = mgr.getDendronInfo(netuid, address)
        
        # 检查是否激活
        if not dendron_info[2]:  # isActive field
            print(f"[yellow]User {address} is not active in subnet {netuid}")
            print(f"[yellow]Status: Not registered or inactive")
            return
        
        # 检查是否是验证者
        is_validator = dendron_info[3]  # isValidator field
        stake_amount = dendron_info[4]  # stake field
        registration_block = dendron_info[5]  # registrationBlock field
        
        stake_hetu = mgr.web3.from_wei(stake_amount, "ether")
        
        if is_validator:
            print(f"[green]User {address} in subnet {netuid}:")
            print(f"[green]  Role: Validator")
            print(f"[green]  Stake: {stake_hetu} HETU")
            print(f"[green]  Registration Block: {registration_block}")
        else:
            print(f"[green]User {address} in subnet {netuid}:")
            print(f"[green]  Role: Miner")
            print(f"[green]  Stake: {stake_hetu} HETU")
            print(f"[green]  Registration Block: {registration_block}")
            
    except Exception as e:
        print(f"[yellow]User {address} is not registered in subnet {netuid}")
        print(f"[yellow]Status: Not joined") 