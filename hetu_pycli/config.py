import os
import yaml
from pathlib import Path

_epilog = "Made with ❤️  by The Hetu protocol"

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.hetucli/config.yml")
DEFAULT_CONFIG = {
    "chain": "ws://127.0.0.1:9090",
    "json_rpc": "http://161.97.161.133:18545",
    "network": "local",
    "no_cache": False,
    "wallet_hotkey": "hotkey-user1",
    "wallet_name": "coldkey-user1",
    "wallet_path": os.path.expanduser("~/.hetucli/wallets"),
    "whetu_address": "0x0000000000000000000000000000000000000000",
    "subnet_address": "0x0000000000000000000000000000000000000000",
    "staking_address": "0x0000000000000000000000000000000000000000",
    "amm_address": "0x0000000000000000000000000000000000000000",
    "dendron_address": "0x0000000000000000000000000000000000000000",
    "weights_address": "0x0000000000000000000000000000000000000000",
    "metagraph_cols": {
        "ACTIVE": True,
        "AXON": True,
        "COLDKEY": True,
        "CONSENSUS": True,
        "DIVIDENDS": True,
        "EMISSION": True,
        "HOTKEY": True,
        "INCENTIVE": True,
        "RANK": True,
        "STAKE": True,
        "TRUST": True,
        "UID": True,
        "UPDATED": True,
        "VAL": True,
        "VTRUST": True,
    },
}


def load_config(config_path: str = None, cli_args: dict = None):
    path = config_path or DEFAULT_CONFIG_PATH
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(path):
        with open(path, "r") as f:
            file_cfg = yaml.safe_load(f) or {}
            config.update(file_cfg)
    if cli_args:
        for k, v in cli_args.items():
            if v is not None:
                config[k] = v
    return config


def ensure_config_file():
    path = Path(DEFAULT_CONFIG_PATH)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.safe_dump(DEFAULT_CONFIG, f)
