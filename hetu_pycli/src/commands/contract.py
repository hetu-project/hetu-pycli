import typer
from web3 import Web3
from rich import print

contract_app = typer.Typer(help="Contract operations")


@contract_app.command()
def call(
    address: str = typer.Option(..., help="Contract address"),
    abi_path: str = typer.Option(..., help="ABI file path"),
    function: str = typer.Option(..., help="Contract method name"),
    args: str = typer.Option("", help="Method arguments, comma separated"),
    rpc: str = typer.Option(..., help="Ethereum node RPC URL"),
):
    """Call contract view method"""
    import json

    w3 = Web3(Web3.HTTPProvider(rpc))
    with open(abi_path, "r") as f:
        abi = json.load(f)
    contract = w3.eth.contract(address=address, abi=abi)
    fn = getattr(contract.functions, function)
    arg_list = [eval(x) for x in args.split(",")] if args else []
    result = fn(*arg_list).call()
    print(f"[cyan]Return value: {result}")
