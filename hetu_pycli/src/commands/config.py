import typer
import yaml
import json
from rich import print
from hetu_pycli.config import DEFAULT_CONFIG_PATH, load_config, ensure_config_file

config_app = typer.Typer(help="Config file management commands")

@config_app.command()
def show(ctx: typer.Context):
    """Displays settings from the config file."""
    typer.echo(json.dumps(ctx.obj, indent=2, ensure_ascii=False))

@config_app.command()
def get(
    key: str = typer.Argument(None, help="Config key (optional, show all if omitted)"),
):
    """Show current config value(s)"""
    ensure_config_file()
    config = load_config()
    if key:
        value = config.get(key, None)
        print(f"[cyan]{key}: {value}")
    else:
        for k, v in config.items():
            print(f"[cyan]{k}: {v}")


@config_app.command()
def set(
    key: str = typer.Argument(..., help="Config key to set/update"),
    value: str = typer.Argument(..., help="Value to set"),
):
    """Set or update a config value"""
    ensure_config_file()
    path = DEFAULT_CONFIG_PATH
    config = load_config()
    config[key] = value
    with open(path, "w") as f:
        yaml.safe_dump(config, f)
    print(f"[green]Set {key} = {value}")


@config_app.command()
def clear(key: str = typer.Argument(..., help="Config key to clear")):
    """Clear a specific config key"""
    ensure_config_file()
    path = DEFAULT_CONFIG_PATH
    config = load_config()
    if key in config:
        del config[key]
        with open(path, "w") as f:
            yaml.safe_dump(config, f)
        print(f"[yellow]Cleared {key}")
    else:
        print(f"[red]Key not found: {key}")
