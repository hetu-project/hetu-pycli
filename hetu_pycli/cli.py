import typer
from typer import Typer
from hetu_pycli.src.commands.wallet import wallet_app
from hetu_pycli.src.commands.tx import tx_app
from hetu_pycli.src.commands.contract import contract_app
from hetu_pycli.src.commands.config import config_app
from hetu_pycli.src.hetu.erc20 import erc20_app
from hetu_pycli.src.hetu.whetu import whetu_app
from hetu_pycli.src.hetu.staking import staking_app
from hetu_pycli.src.hetu.subnet import subnet_app
from hetu_pycli.src.hetu.amm import amm_app
from hetu_pycli.src.hetu.neuron import neuron_app
from hetu_pycli.config import load_config, ensure_config_file, _epilog
from hetu_pycli.version import __version__

app = Typer(
    help="Hetu chain command line client",
    no_args_is_help=True,
    epilog=_epilog
)

@app.callback()
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        callback=lambda v: (print(__version__), raise_exit()) if v else None,
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
    ctx.obj = config_obj


def raise_exit():
    raise typer.Exit()


app.add_typer(
    wallet_app,
    name="wallet",
    help="Wallet management",
    no_args_is_help=True,
    epilog=_epilog
)
app.add_typer(wallet_app, name="w", hidden=True, no_args_is_help=True)
app.add_typer(tx_app, name="tx", help="Transfer & transaction", no_args_is_help=True, epilog=_epilog)
app.add_typer(
    contract_app, name="contract", help="Contract operations", no_args_is_help=True, epilog=_epilog
)
app.add_typer(config_app, name="config", help="Config management", no_args_is_help=True, epilog=_epilog)
app.add_typer(config_app, name="c", hidden=True, no_args_is_help=True)
app.add_typer(config_app, name="conf", hidden=True, no_args_is_help=True)
app.add_typer(erc20_app, name="erc20", help="ERC20 token operations", no_args_is_help=True, epilog=_epilog)
app.add_typer(whetu_app, name="whetu", help="WHETU contract operations", no_args_is_help=True, epilog=_epilog)
app.add_typer(staking_app, name="stake", help="Global staking operations", no_args_is_help=True, epilog=_epilog)
app.add_typer(subnet_app, name="subnet", help="Subnet manager operations", no_args_is_help=True, epilog=_epilog)
app.add_typer(amm_app, name="amm", help="Subnet AMM operations", no_args_is_help=True, epilog=_epilog)
app.add_typer(neuron_app, name="neuron", help="Neuron manager operations", no_args_is_help=True, epilog=_epilog)

if __name__ == "__main__":
    app()
