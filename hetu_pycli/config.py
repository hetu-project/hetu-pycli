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
    "whetu_address": "0xBC45C2511eA43F998E659b4722D6795C482a7E07",
    "subnet_address": "0xaF856443EaF741eEcAD2b5Bb3ff6F9F57a00920F",
    "staking_address": "0x9cCb4A38a208409422969737977696B8189eF96a",
    "amm_address": "0x36607E8D2cb850E3b2d14b998A25c43611d710cE",
    "dendron_address": "0x34d3911323Ef5576Ba84a5a68b814D189112020F",
    "weights_address": "0x1011c3586a901FBea4DEB3df16cFC42922219D86",
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
