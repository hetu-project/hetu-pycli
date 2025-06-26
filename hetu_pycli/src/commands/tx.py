import typer
from web3 import Web3
from eth_account import Account
from rich import print

tx_app = typer.Typer(help="Transfer and transaction commands")


@tx_app.command()
def send(
    private_key: str = typer.Option(..., help="Sender private key"),
    to: str = typer.Option(..., help="Recipient address"),
    value: float = typer.Option(..., help="Transfer amount (ETH)"),
    rpc: str = typer.Option(..., help="Ethereum node RPC URL"),
):
    """Send ETH transfer"""
    w3 = Web3(Web3.HTTPProvider(rpc))
    acct = Account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = {
        "to": to,
        "value": w3.to_wei(value, "ether"),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
    }
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"[green]Transaction sent: {tx_hash.hex()}")
