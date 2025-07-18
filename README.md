<div align="center">

# Hetu Chain CLI <!-- omit in toc -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Twitter](https://img.shields.io/badge/Twitter-@hetu_protocol-1DA1F2?logo=twitter&logoColor=white)](https://x.com/hetu_protocol)
<!-- [![PyPI version](https://badge.fury.io/py/hetu_pycli.svg)](https://badge.fury.io/py/hetu_pycli) -->

---

### Causality Graph Future In Web3 

 [SDK](https://github.com/hetu-project/hetu-pysdk) • [Chain](https://github.com/hetu-project/hetu-chain) • [Research](https://docsend.com/v/jt55f/hetu_litepaper)


</div>

---

The Hetu CLI, `hetucli`, is a powerful command line tool for interacting with the Hetu blockchain. You can use it on any macOS, Linux, or WSL terminal to manage wallets, transfer HETU, query balances, interact with smart contracts, and more. Help information can be invoked for every command and option with `--help`.

## Documentation

Installation steps are described below. For full documentation on how to use `hetucli`, see the [Hetu CLI section](https://github.com/hetu-project/hetu-pycli#readme) on the developer documentation site.

---

## Features
- Wallet management (create, query balance, export private key)
- HETU transfer, signing, send transaction
- Query on-chain balance
- Contract call (read-only)
- Command line powered by Typer

---

## Install on macOS and Linux

You can install `hetucli` on your local machine directly from source or PyPI. **Make sure you verify your installation after you install**:

### Install from [PyPI](https://pypi.org/project/hetu-pycli/)

Run
```bash
pip install -U hetu-pycli
```

### Install from source

1. Clone the Hetu CLI repo.

```bash
git clone https://github.com/hetu-project/hetu-pycli.git
```

2. `cd` into `hetu-pycli` directory.

```bash
cd hetu-pycli
```

3. Create and activate a virtual environment.

```bash
make init-venv
```
4. Install dependencies and the CLI:

Using Poetry
```bash
pip install -U pip setuptools poetry
poetry install
```

Or, using Pip:
```bash
pip install .
```


---

## Usage

You can invoke the CLI using the following command:

```bash
python -m hetu_pycli.cli --help
```

Or, if installed as a script:

```bash
hetucli --help
```

### Wallet management
```bash
hetucli wallet create
hetucli wallet balance <address> --rpc <rpc_url>
```

### Transfer
```bash
hetucli tx send --private-key <key> --to <address> --value <hetu> --rpc <rpc_url>
```

### Configuration

Set the contract address

```bash
hetucli c set whetu_address <address>
hetucli c set staking_address <address>
hetucli c set subnet_address <address>
hetucli c set whetu_address <address>
```

### WHETU

```bash
hetucli whetu deposit --contract <address> --sender <address> --value <amount>
hetucli whetu withdraw --contract <address> --sender <address> --amount <amount>
hetucli whetu balance-of --contract <address> --account <address>
hetucli whetu transfer --contract <address> --to <address> --value <amount> --sender <address>
hetucli whetu approve --contract <address> --spender <address> --value <amount> --sender <address>
hetucli whetu total-eth --contract <address>
hetucli whetu total-supply --contract <address>
hetucli whetu nonces --contract <address> --owner <address>
```

### Staking, Subnet, Swap

```bash
hetucli stake total-staked --contract <address>
hetucli stake add-stake --contract <address> --sender <address> --amount <amount>
hetucli subnet next-netuid --contract <address>
hetucli subnet register-network --contract <address> --sender <address> --name ... --description ... --token-name ... --token-symbol ...
hetucli amm alpha-price --contract <address>
hetucli amm swap-hetu-for-alpha --contract <address> --sender <address> --hetu-amount-in <amount> --alpha-amount-out-min <amount> --to <address>
```

### Contract call
```bash
hetucli contract call --address <contract_addr> --abi-path <abi.json> --function <fn> --args "1,2,3" --rpc <rpc_url>
```

---

## Running Tests & Development
To run the tests, ensure you have the Hetu CLI installed and configured. Then, execute:

```bash
poetry run pytest tests
```

---

## License

This project is licensed under the MIT License.
