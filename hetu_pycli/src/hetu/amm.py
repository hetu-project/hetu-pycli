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

def get_amm_contract_address(ctx, contract: str, netuid: int, subnet_contract: str = None):
    """Get AMM contract address from either contract parameter or netuid"""
    if contract and netuid:
        print("[red]Cannot specify both contract and netuid. Please use only one.")
        raise typer.Exit(1)
    
    if not contract and not netuid:
        print("[red]Must specify either contract or netuid.")
        raise typer.Exit(1)
    
    if contract:
        # Use direct contract address
        return get_contract_address(ctx, "amm_address", contract)
    else:
        # Get AMM contract address from netuid
        rpc = ctx.obj.get("json_rpc") if ctx.obj else None
        if not rpc:
            print("[red]No RPC URL found in config or CLI.")
            raise typer.Exit(1)
        
        # Load subnet manager to get AMM pool address
        from hetu_pycli.src.hetu.subnet import load_subnet_mgr
        subnet_contract = get_contract_address(ctx, "subnet_address", subnet_contract)
        subnet_mgr = load_subnet_mgr(subnet_contract, rpc)
        
        # Get subnet info to extract AMM pool address
        subnet_info = subnet_mgr.getSubnetInfo(netuid)
        amm_pool_address = subnet_info[3]  # AMM Pool address is at index 3
        
        if amm_pool_address == "0x0000000000000000000000000000000000000000":
            print(f"[red]No AMM pool found for netuid {netuid}")
            raise typer.Exit(1)
        
        print(f"[yellow]AMM Pool Address from netuid {netuid}: {amm_pool_address}")
        return amm_pool_address

@amm_app.command()
def alpha_price(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
):
    """Query current alpha price"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
    amm = load_amm(amm_contract, rpc)
    alpha_price_wei = amm.getAlphaPrice()
    
    # Convert wei to ether for better readability
    alpha_price_ether = amm.web3.from_wei(alpha_price_wei, "ether")
    
    print(f"[green]Alpha Price:")
    print(f"  Raw (wei): {alpha_price_wei}")
    print(f"  Formatted: {alpha_price_ether} ALPHA/HETU")
    
    # Show the exchange rate
    if alpha_price_ether == 1.0:
        print(f"  Exchange Rate: 1 ALPHA = 1 HETU (1:1)")
    else:
        hetu_per_alpha = alpha_price_ether
        alpha_per_hetu = 1 / alpha_price_ether
        print(f"  Exchange Rate: 1 ALPHA = {hetu_per_alpha:.6f} HETU")
        print(f"               1 HETU = {alpha_per_hetu:.6f} ALPHA")

@amm_app.command()
def pool_info(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
):
    """Query pool info"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
    amm = load_amm(amm_contract, rpc)
    pool = amm.getPoolInfo()
    print(f"[green]Pool Info: \n- mechanism: {pool[0]}\n- subnetTAO: {pool[1]}\n- subnetAlphaIn: {pool[2]}\n- subnetAlphaOut: {pool[3]}\n- currentPrice: {pool[4]}\n- movingPrice: {pool[5]}\n- totalVolume: {pool[6]}\n- minimumLiquidity: {pool[7]}")

@amm_app.command()
def statistics(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
):
    """Query pool statistics"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
    amm = load_amm(amm_contract, rpc)
    print(f"[green]Statistics: {amm.getStatistics()}")

@amm_app.command()
def swap_preview(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
    amount_in: float = typer.Option(..., help="Input amount (in HETU or ALPHA)"),
    is_hetu_to_alpha: bool = typer.Option(..., help="True for HETU->ALPHA, False for ALPHA->HETU"),
):
    """Preview swap result and price impact"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
    amm = load_amm(amm_contract, rpc)
    amount_in_wei = amm.web3.to_wei(amount_in, "ether")
    print(f"[green]Swap Preview: {amm.getSwapPreview(amount_in_wei, is_hetu_to_alpha)}")

@amm_app.command()
def sim_swap_alpha_for_hetu(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
    alpha_amount: float = typer.Option(..., help="Alpha amount (in ALPHA)"),
):
    """Simulate swap ALPHA for HETU"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
    amm = load_amm(amm_contract, rpc)
    alpha_amount_wei = amm.web3.to_wei(alpha_amount, "ether")
    print(f"[green]Simulated HETU Out: {amm.simSwapAlphaForHETU(alpha_amount_wei)}")

@amm_app.command()
def sim_swap_hetu_for_alpha(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
    hetu_amount: float = typer.Option(..., help="HETU amount (in HETU)"),
):
    """Simulate swap HETU for ALPHA"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
    amm = load_amm(amm_contract, rpc)
    hetu_amount_wei = amm.web3.to_wei(hetu_amount, "ether")
    print(f"[green]Simulated ALPHA Out: {amm.simSwapHETUForAlpha(hetu_amount_wei)}")

@amm_app.command()
def inject_liquidity(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    hetu_amount: float = typer.Option(..., help="HETU amount to add (in HETU)"),
    alpha_amount: float = typer.Option(..., help="ALPHA amount to add (in ALPHA)"),
):
    """Inject liquidity into the pool"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
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
    amm = load_amm(amm_contract, rpc)
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
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    hetu_amount: float = typer.Option(..., help="HETU amount to withdraw (in HETU)"),
    alpha_amount: float = typer.Option(..., help="ALPHA amount to withdraw (in ALPHA)"),
    to: str = typer.Option(None, help="Recipient address (defaults to sender address)"),
):
    """Withdraw liquidity from the pool"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
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
    
    # Use sender address as default recipient if not specified
    recipient = to or keystore["address"]
    if not to:
        print(f"[yellow]Using sender address as recipient: {recipient}")
    
    amm = load_amm(amm_contract, rpc)
    from_address = keystore["address"]
    nonce = amm.web3.eth.get_transaction_count(from_address)
    hetu_amount_wei = amm.web3.to_wei(hetu_amount, "ether")
    alpha_amount_wei = amm.web3.to_wei(alpha_amount, "ether")
    tx = amm.contract.functions.withdrawLiquidity(hetu_amount_wei, alpha_amount_wei, recipient).build_transaction(
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
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    alpha_amount_in: float = typer.Option(..., help="Alpha amount in (in ALPHA)"),
    hetu_amount_out_min: float = typer.Option(..., help="Minimum HETU out (in HETU)"),
    to: str = typer.Option(None, help="Recipient address (defaults to sender address)"),
):
    """Swap ALPHA for HETU"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
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
    
    # Use sender address as default recipient if not specified
    recipient = to or keystore["address"]
    if not to:
        print(f"[yellow]Using sender address as recipient: {recipient}")
    
    amm = load_amm(amm_contract, rpc)
    from_address = keystore["address"]
    nonce = amm.web3.eth.get_transaction_count(from_address)
    alpha_amount_in_wei = amm.web3.to_wei(alpha_amount_in, "ether")
    hetu_amount_out_min_wei = amm.web3.to_wei(hetu_amount_out_min, "ether")
    tx = amm.contract.functions.swapAlphaForHETU(alpha_amount_in_wei, hetu_amount_out_min_wei, recipient).build_transaction(
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
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    hetu_amount_in: float = typer.Option(..., help="HETU amount in (in HETU)"),
    alpha_amount_out_min: float = typer.Option(..., help="Minimum ALPHA out (in ALPHA)"),
    to: str = typer.Option(None, help="Recipient address (defaults to sender address)"),
):
    """Swap HETU for ALPHA"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
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
    
    # Use sender address as default recipient if not specified
    recipient = to or keystore["address"]
    if not to:
        print(f"[yellow]Using sender address as recipient: {recipient}")
    
    amm = load_amm(amm_contract, rpc)
    from_address = keystore["address"]
    nonce = amm.web3.eth.get_transaction_count(from_address)
    hetu_amount_in_wei = amm.web3.to_wei(hetu_amount_in, "ether")
    alpha_amount_out_min_wei = amm.web3.to_wei(alpha_amount_out_min, "ether")
    tx = amm.contract.functions.swapHETUForAlpha(hetu_amount_in_wei, alpha_amount_out_min_wei, recipient).build_transaction(
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

@amm_app.command()
def approve_tokens(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    hetu_amount: float = typer.Option(None, help="HETU amount to approve (in HETU)"),
    alpha_amount: float = typer.Option(None, help="ALPHA amount to approve (in ALPHA)"),
):
    """Approve AMM contract to spend your tokens"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
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
    
    amm = load_amm(amm_contract, rpc)
    from_address = keystore["address"]
    
    # Get token addresses from AMM contract
    hetu_token_address = amm.hetuToken()
    alpha_token_address = amm.alphaToken()
    
    print(f"[yellow]AMM Contract: {amm_contract}")
    print(f"[yellow]HETU Token: {hetu_token_address}")
    print(f"[yellow]ALPHA Token: {alpha_token_address}")
    
    # Load token contracts
    from hetu_pycli.src.hetu.erc20 import load_erc20
    
    if hetu_amount is not None:
        print(f"[green]Approving HETU tokens...")
        hetu_token = load_erc20(hetu_token_address, rpc)
        hetu_amount_wei = hetu_token.web3.to_wei(hetu_amount, "ether")
        
        nonce = hetu_token.web3.eth.get_transaction_count(from_address)
        tx = hetu_token.contract.functions.approve(amm_contract, hetu_amount_wei).build_transaction(
            {
                "from": from_address,
                "nonce": nonce,
                "gas": 100000,
                "gasPrice": hetu_token.web3.eth.gas_price,
            }
        )
        signed = hetu_token.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = hetu_token.web3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"[green]Broadcasted HETU approve tx hash: {tx_hash.hex()}")
        print("[yellow]Waiting for transaction receipt...")
        receipt = hetu_token.web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print(f"[green]HETU approve succeeded in block {receipt.blockNumber}")
        else:
            print(f"[red]HETU approve failed in block {receipt.blockNumber}")
    
    if alpha_amount is not None:
        print(f"[green]Approving ALPHA tokens...")
        alpha_token = load_erc20(alpha_token_address, rpc)
        alpha_amount_wei = alpha_token.web3.to_wei(alpha_amount, "ether")
        
        nonce = alpha_token.web3.eth.get_transaction_count(from_address)
        tx = alpha_token.contract.functions.approve(amm_contract, alpha_amount_wei).build_transaction(
            {
                "from": from_address,
                "nonce": nonce,
                "gas": 100000,
                "gasPrice": alpha_token.web3.eth.gas_price,
            }
        )
        signed = alpha_token.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = alpha_token.web3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"[green]Broadcasted ALPHA approve tx hash: {tx_hash.hex()}")
        print("[yellow]Waiting for transaction receipt...")
        receipt = alpha_token.web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print(f"[green]ALPHA approve succeeded in block {receipt.blockNumber}")
        else:
            print(f"[red]ALPHA approve failed in block {receipt.blockNumber}")
    
    if hetu_amount is None and alpha_amount is None:
        print("[yellow]No amounts specified. Use --hetu-amount or --alpha-amount to approve tokens.")

@amm_app.command()
def check_approval(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
):
    """Check token approval and balance status"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
    config = ctx.obj
    wallet_path = wallet_path or get_wallet_path(config)
    keystore = load_keystore(sender, wallet_path)
    from_address = keystore["address"]
    
    amm = load_amm(amm_contract, rpc)
    
    # Get token addresses from AMM contract
    hetu_token_address = amm.hetuToken()
    alpha_token_address = amm.alphaToken()
    
    print(f"[yellow]AMM Contract: {amm_contract}")
    print(f"[yellow]User Address: {from_address}")
    print(f"[yellow]HETU Token: {hetu_token_address}")
    print(f"[yellow]ALPHA Token: {alpha_token_address}")
    
    # Load token contracts
    from hetu_pycli.src.hetu.erc20 import load_erc20
    
    # Check HETU token
    hetu_token = load_erc20(hetu_token_address, rpc)
    hetu_balance = hetu_token.balanceOf(from_address)
    hetu_allowance = hetu_token.allowance(from_address, amm_contract)
    hetu_balance_ether = hetu_token.web3.from_wei(hetu_balance, "ether")
    hetu_allowance_ether = hetu_token.web3.from_wei(hetu_allowance, "ether")
    
    print(f"\n[green]HETU Token Status:")
    print(f"  Balance: {hetu_balance_ether} HETU")
    print(f"  Allowance: {hetu_allowance_ether} HETU")
    print(f"  Raw Balance: {hetu_balance}")
    print(f"  Raw Allowance: {hetu_allowance}")
    
    # Check ALPHA token
    alpha_token = load_erc20(alpha_token_address, rpc)
    alpha_balance = alpha_token.balanceOf(from_address)
    alpha_allowance = alpha_token.allowance(from_address, amm_contract)
    alpha_balance_ether = alpha_token.web3.from_wei(alpha_balance, "ether")
    alpha_allowance_ether = alpha_token.web3.from_wei(alpha_allowance, "ether")
    
    print(f"\n[green]ALPHA Token Status:")
    print(f"  Balance: {alpha_balance_ether} ALPHA")
    print(f"  Allowance: {alpha_allowance_ether} ALPHA")
    print(f"  Raw Balance: {alpha_balance}")
    print(f"  Raw Allowance: {alpha_allowance}")
    
    # Check AMM pool status
    pool_info = amm.getPoolInfo()
    print(f"\n[green]AMM Pool Status:")
    print(f"  Mechanism: {pool_info[0]}")
    print(f"  HETU Reserve: {pool_info[1]}")
    print(f"  ALPHA Reserve: {pool_info[2]}")
    print(f"  ALPHA Out: {pool_info[3]}")
    print(f"  Current Price: {pool_info[4]}")
    print(f"  Moving Price: {pool_info[5]}")
    
    # Simulate swap
    hetu_amount_wei = hetu_token.web3.to_wei(10.0, "ether")
    simulated_alpha = amm.simSwapHETUForAlpha(hetu_amount_wei)
    simulated_alpha_ether = hetu_token.web3.from_wei(simulated_alpha, "ether")
    
    print(f"\n[green]Swap Simulation (10 HETU):")
    print(f"  Expected ALPHA Out: {simulated_alpha_ether}")
    print(f"  Raw Expected: {simulated_alpha}")
    
    # Check if swap would succeed
    if hetu_balance < hetu_amount_wei:
        print(f"[red]❌ Insufficient HETU balance")
    else:
        print(f"[green]✅ Sufficient HETU balance")
    
    if hetu_allowance < hetu_amount_wei:
        print(f"[red]❌ Insufficient HETU allowance")
    else:
        print(f"[green]✅ Sufficient HETU allowance")
    
    if simulated_alpha == 0:
        print(f"[red]❌ Swap simulation failed - no liquidity or other issue")
    else:
        print(f"[green]✅ Swap simulation successful")

@amm_app.command()
def pool_status(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="AMM contract address"),
    netuid: int = typer.Option(None, help="Subnet netuid"),
    subnet_contract: str = typer.Option(None, help="Subnet manager contract address (required when using netuid)"),
):
    """Check AMM pool system status and initialization"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    amm_contract = get_amm_contract_address(ctx, contract, netuid, subnet_contract)
    amm = load_amm(amm_contract, rpc)
    
    print(f"[yellow]AMM Pool Status Check:")
    print(f"  Contract: {amm_contract}")
    
    # Get system info
    system_info = amm.getSystemInfo()
    print(f"\n[green]System Information:")
    print(f"  System Address: {system_info[0]}")
    print(f"  Subnet Contract: {system_info[1]}")
    
    # Get creator info
    creator_info = amm.getCreatorInfo()
    print(f"\n[green]Creator Information:")
    print(f"  Creator: {creator_info[0]}")
    print(f"  Created At: {creator_info[1]}")
    print(f"  Netuid: {creator_info[2]}")
    
    # Get pool info
    pool_info = amm.getPoolInfo()
    print(f"\n[green]Pool Information:")
    print(f"  Mechanism: {pool_info[0]} (0=Stable, 1=Dynamic)")
    print(f"  HETU Reserve: {pool_info[1]}")
    print(f"  ALPHA Reserve: {pool_info[2]}")
    print(f"  ALPHA Out: {pool_info[3]}")
    print(f"  Current Price: {pool_info[4]}")
    print(f"  Moving Price: {pool_info[5]}")
    print(f"  Total Volume: {pool_info[6]}")
    print(f"  Min Liquidity: {pool_info[7]}")
    
    # Get token addresses
    hetu_token = amm.hetuToken()
    alpha_token = amm.alphaToken()
    print(f"\n[green]Token Addresses:")
    print(f"  HETU Token: {hetu_token}")
    print(f"  ALPHA Token: {alpha_token}")
    
    # Check if pool is initialized
    hetu_reserve = pool_info[1]
    alpha_reserve = pool_info[2]
    min_liquidity = pool_info[7]
    
    print(f"\n[green]Initialization Status:")
    if hetu_reserve >= min_liquidity and alpha_reserve >= min_liquidity:
        print(f"  ✅ Pool is properly initialized")
    else:
        print(f"  ❌ Pool needs initialization")
        print(f"  Required minimum liquidity: {min_liquidity}")
        print(f"  Current HETU reserve: {hetu_reserve}")
        print(f"  Current ALPHA reserve: {alpha_reserve}")
    
    # Check mechanism type
    mechanism = pool_info[0]
    if mechanism == 0:
        print(f"  Mechanism: Stable (1:1 exchange)")
    else:
        print(f"  Mechanism: Dynamic (AMM exchange)")
    
    # Check if trading is possible
    if hetu_reserve > 0 and alpha_reserve > 0:
        print(f"  ✅ Trading is possible")
    else:
        print(f"  ❌ Trading is not possible - insufficient liquidity") 