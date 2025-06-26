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

### Contract call
```bash
hetucli contract call --address <contract_addr> --abi-path <abi.json> --function <fn> --args "1,2,3" --rpc <rpc_url>
```

---

## License

This project is licensed under the MIT License.
