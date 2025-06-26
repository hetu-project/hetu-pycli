import typer
from typer import Typer
from hetu_pycli.src.commands.wallet import wallet_app
from hetu_pycli.src.commands.tx import tx_app
from hetu_pycli.src.commands.contract import contract_app
from hetu_pycli.config import load_config, ensure_config_file
from hetu_pycli.version import __version__

app = Typer(
    help="Hetu chain command line client",
    no_args_is_help=True,
)


@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        callback=lambda v: (print(__version__), raise_exit())
        if v
        else None,
        is_eager=True,
        help="Show version and exit.",
    ),
    config: str = typer.Option(
        None, help="Config file path, default ~/.hetucli/config.yml"
    ),
    chain: str = typer.Option(None, help="Chain RPC URL"),
    network: str = typer.Option(None, help="Network name"),
    no_cache: bool = typer.Option(None, help="Disable cache"),
    wallet_hotkey: str = typer.Option(None, help="Wallet hotkey name"),
    wallet_name: str = typer.Option(None, help="Wallet name"),
    wallet_path: str = typer.Option("~/.hetucli/wallets", help="Wallet path"),
):
    """Hetu CLI entry, loads config and merges CLI args."""
    ensure_config_file()
    cli_args = dict(
        chain=chain,
        network=network,
        no_cache=no_cache,
        wallet_hotkey=wallet_hotkey,
        wallet_name=wallet_name,
        wallet_path=wallet_path,
    )
    config_obj = load_config(config, cli_args)
    typer.Context.obj = config_obj


def raise_exit():
    raise typer.Exit()


app.add_typer(wallet_app, name="wallet", help="Wallet management")
app.add_typer(tx_app, name="tx", help="Transfer & transaction")
app.add_typer(contract_app, name="contract", help="Contract operations")

if __name__ == "__main__":
    app()
