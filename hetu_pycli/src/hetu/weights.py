import typer
from rich import print
from web3 import Web3
import json
import os
from .wrapper.weights import Weights
from eth_account import Account
from hetu_pycli.src.commands.wallet import load_keystore, get_wallet_path
import getpass

WEIGHTS_ABI_PATH = os.path.join(
    os.path.dirname(__file__), "../../../contracts/Weights.abi"
)

weights_app = typer.Typer(help="Weights contract operations for validator scoring")

def get_contract_address(ctx, cli_contract_key: str, param_contract: str):
    config = ctx.obj or {}
    contract_addr = param_contract or config.get(cli_contract_key)
    if not contract_addr:
        print(f"[red]No contract address provided or found in config for {cli_contract_key}.")
        raise typer.Exit(1)
    print(f"[yellow]Using contract address: {contract_addr}")
    return contract_addr

def load_weights(contract: str, rpc: str):
    abi_path = os.path.abspath(WEIGHTS_ABI_PATH)
    if not os.path.exists(abi_path):
        print(f"[red]ABI file not found: {abi_path}")
        raise typer.Exit(1)
    with open(abi_path, "r") as f:
        abi = json.load(f)
    provider = Web3.HTTPProvider(rpc)
    return Weights(contract, provider, abi)

@weights_app.command()
def set_weights(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Weights contract address (default from config)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    weights_file: str = typer.Option(None, help="JSON file containing weights data"),
    weights_json: str = typer.Option(None, help="JSON string containing weights data"),
):
    """Set weights for nodes in a subnet (validator only)"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "weights_address", contract)
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
    
    # Load weights contract
    weights_contract = load_weights(contract, rpc)
    
    # Parse weights data
    weights_data = []
    if weights_file:
        try:
            with open(weights_file, 'r') as f:
                weights_data = json.load(f)
            print(f"[green]Loaded weights from file: {weights_file}")
        except Exception as e:
            print(f"[red]Failed to load weights file: {e}")
            raise typer.Exit(1)
    elif weights_json:
        try:
            weights_data = json.loads(weights_json)
            print(f"[green]Loaded weights from JSON string")
        except Exception as e:
            print(f"[red]Failed to parse weights JSON: {e}")
            raise typer.Exit(1)
    else:
        print("[red]Please provide either --weights-file or --weights-json")
        raise typer.Exit(1)
    
    # Validate weights data structure
    if not isinstance(weights_data, list):
        print("[red]Weights data must be a list")
        raise typer.Exit(1)
    
    # Convert weights data to contract format
    contract_weights = []
    for weight in weights_data:
        if not isinstance(weight, dict) or 'dest' not in weight or 'weight' not in weight:
            print(f"[red]Invalid weight format: {weight}")
            print("[red]Each weight must have 'dest' (address) and 'weight' (uint256) fields")
            raise typer.Exit(1)
        
        dest = weight['dest']
        weight_value = weight['weight']
        
        # Validate address format
        if not Web3.is_address(dest):
            print(f"[red]Invalid destination address: {dest}")
            raise typer.Exit(1)
        
        # Validate weight value (0 to 1e6 representing 0 to 1)
        if not isinstance(weight_value, (int, float)) or weight_value < 0 or weight_value > 1000000:
            print(f"[red]Invalid weight value: {weight_value}")
            print("[red]Weight must be between 0 and 1000000 (representing 0 to 1)")
            raise typer.Exit(1)
        
        contract_weights.append([dest, int(weight_value)])
    
    print(f"[green]Setting weights for subnet {netuid}")
    print(f"[green]Number of weights: {len(contract_weights)}")
    for i, (dest, weight) in enumerate(contract_weights):
        weight_normalized = weight / 1000000.0
        print(f"[green]  {i+1}. {dest} -> {weight} ({weight_normalized:.6f})")
    
    # Build transaction
    nonce = weights_contract.web3.eth.get_transaction_count(from_address)
    
    # Prepare weights data for contract call - combine dests and weights into Weight struct array
    new_weights = []
    for dest, weight in contract_weights:
        new_weights.append([dest, weight])  # [address, uint256] format for Weight struct
    
    tx = weights_contract.contract.functions.setWeights(netuid, new_weights).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": weights_contract.web3.eth.gas_price,
        }
    )
    
    signed = weights_contract.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = weights_contract.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted setWeights tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    
    receipt = weights_contract.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]SetWeights succeeded in block {receipt.blockNumber}")
        print(f"[green]Weights updated for subnet {netuid}")
    else:
        print(f"[red]SetWeights failed in block {receipt.blockNumber}, receipt {receipt}")

@weights_app.command()
def get_weights(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Weights contract address (default from config)"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    validator: str = typer.Option(..., help="Validator address"),
    dest: str = typer.Option(..., help="Destination address"),
):
    """Query weights for a specific validator-destination pair in a subnet"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "weights_address", contract)
    if not rpc:
        print("[red]No RPC URL found in config or CLI.")
        raise typer.Exit(1)
    
    weights_contract = load_weights(contract, rpc)
    
    # Validate addresses
    if not Web3.is_address(validator):
        print(f"[red]Invalid validator address: {validator}")
        raise typer.Exit(1)
    
    if not Web3.is_address(dest):
        print(f"[red]Invalid destination address: {dest}")
        raise typer.Exit(1)
    
    try:
        weight = weights_contract.weights(netuid, validator, dest)
        weight_normalized = weight / 1000000.0
        print(f"[green]Weight for subnet {netuid}, validator {validator}, destination {dest}:")
        print(f"[green]  Raw weight: {weight}")
        print(f"[green]  Normalized weight: {weight_normalized:.6f} (0-1 scale)")
    except Exception as e:
        print(f"[red]Failed to get weight: {e}")
        raise typer.Exit(1)

@weights_app.command()
def create_weights_template(
    ctx: typer.Context,
    output_file: str = typer.Option("weights_template.json", help="Output file name"),
):
    """Create a template JSON file for weights data"""
    template = [
        {
            "dest": "0x1234567890123456789012345678901234567890",
            "weight": 500000
        },
        {
            "dest": "0x0987654321098765432109876543210987654321",
            "weight": 750000
        }
    ]
    
    try:
        with open(output_file, 'w') as f:
            json.dump(template, f, indent=2)
        print(f"[green]Weights template created: {output_file}")
        print(f"[yellow]Template contains example weights:")
        print(f"[yellow]  - Weight 500000 = 0.5 (50%)")
        print(f"[yellow]  - Weight 750000 = 0.75 (75%)")
        print(f"[yellow]  - Weight range: 0-1000000 (representing 0-1)")
        print(f"[yellow]Edit the file with your actual destination addresses and weights")
    except Exception as e:
        print(f"[red]Failed to create template: {e}")
        raise typer.Exit(1) 

@weights_app.command()
def quick_score(
    ctx: typer.Context,
    contract: str = typer.Option(None, help="Weights contract address (default from config)"),
    sender: str = typer.Option(..., help="Sender address (must match keystore address or wallet name)"),
    wallet_path: str = typer.Option(None, help="Wallet path (default from config)"),
    password: str = typer.Option(None, hide_input=True, help="Keystore password"),
    netuid: int = typer.Option(..., help="Subnet netuid"),
    targets: str = typer.Option(..., help="Comma-separated list of target addresses"),
    scores: str = typer.Option(..., help="Comma-separated list of scores (0-1000000, representing 0-1)"),
):
    """Quick score command for testing - directly input targets and scores"""
    rpc = ctx.obj.get("json_rpc") if ctx.obj else None
    contract = get_contract_address(ctx, "weights_address", contract)
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
    
    # Load weights contract
    weights_contract = load_weights(contract, rpc)
    
    # Parse targets and scores
    target_list = [addr.strip() for addr in targets.split(",")]
    score_list = [score.strip() for score in scores.split(",")]
    
    if len(target_list) != len(score_list):
        print("[red]Number of targets and scores must match")
        raise typer.Exit(1)
    
    # Validate and convert data
    contract_weights = []
    for i, (target, score) in enumerate(zip(target_list, score_list)):
        # Validate address format
        if not Web3.is_address(target):
            print(f"[red]Invalid target address at position {i+1}: {target}")
            raise typer.Exit(1)
        
        # Validate and convert score
        try:
            score_value = int(score)
            if score_value < 0 or score_value > 1000000:
                print(f"[red]Invalid score at position {i+1}: {score}")
                print("[red]Score must be between 0 and 1000000 (representing 0 to 1)")
                raise typer.Exit(1)
        except ValueError:
            print(f"[red]Invalid score format at position {i+1}: {score}")
            raise typer.Exit(1)
        
        contract_weights.append([target, score_value])
    
    print(f"[green]Setting weights for subnet {netuid}")
    print(f"[green]Number of weights: {len(contract_weights)}")
    for i, (target, score) in enumerate(contract_weights):
        score_normalized = score / 1000000.0
        print(f"[green]  {i+1}. {target} -> {score} ({score_normalized:.6f})")
    
    # Build transaction
    nonce = weights_contract.web3.eth.get_transaction_count(from_address)
    
    # Prepare weights data for contract call - combine dests and weights into Weight struct array
    new_weights = []
    for dest, weight in contract_weights:
        new_weights.append([dest, weight])  # [address, uint256] format for Weight struct
    
    tx = weights_contract.contract.functions.setWeights(netuid, new_weights).build_transaction(
        {
            "from": from_address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": weights_contract.web3.eth.gas_price,
        }
    )
    
    signed = weights_contract.web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = weights_contract.web3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"[green]Broadcasted setWeights tx hash: {tx_hash.hex()}")
    print("[yellow]Waiting for transaction receipt...")
    
    receipt = weights_contract.web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"[green]SetWeights succeeded in block {receipt.blockNumber}")
        print(f"[green]Weights updated for subnet {netuid}")
    else:
        print(f"[red]SetWeights failed in block {receipt.blockNumber}, receipt {receipt}") 