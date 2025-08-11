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
hetucli --help
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
# Using wallet name (recommended)
hetucli tx send --sender <wallet_name> --to <address> --value <hetu> --rpc <rpc_url>

# Direct private key usage (not recommended, private key will be exposed in command history)
hetucli tx send-dk --private-key <key> --to <address> --value <hetu> --rpc <rpc_url>
```

### Configuration

Set the contract address

```bash
hetucli c set whetu_address <address>
hetucli c set staking_address <address>
hetucli c set subnet_address <address>
hetucli c set neuron_address <address>
hetucli c set amm_address <address>
```

### Main Process(New,Staking,Swap)

#### New A Subnet

```bash
hetucli w import <private-key> --name test0
hetucli whetu deposit  --sender test0 --value  1000
hetucli whetu balance-of  test0
hetucli subnet get-network-lock-cost
hetucli whetu approve --spender <subnet_address>  --value 100 --sender test0 
hetucli subnet update-network-params --network-min-lock 100000000000000000000  --network-rate-limit 1 --lock-reduction-interval 10000  --sender <address>
hetucli subnet regist --sender test0 --name "AI Vision" --description "Computer vision and image processing network" --token-name "VISION" --token-symbol "VIS"
```

#### Activate Subnet

```bash
# Check subnet status
hetucli subnet subnet-info --netuid <netuid>

# Activate the subnet
hetucli subnet activate-subnet --netuid <netuid> --sender <wallet_name>

# Verify activation status
hetucli subnet subnet-info --netuid <netuid>
```

#### Staking and Participation

```bash
hetucli whetu approve --spender <stake_address>  --value 100 --sender test0
hetucli stake add-stake --sender test0 --amount 100
hetucli stake total-staked
hetucli stake allocate-to-subnet --netuid 1  --sender test0 --amount 50
hetucli neuron regist --sender test0 --netuid 1 --is-validator-role  --axon-endpoint "http://my-node.com" --axon-port 8080 --prometheus-endpoint "http://my-metrics.com" --prometheus-port 9090
```

#### Trading Subnet Tokens

```bash
hetucli subnet subnet-info --netuid 1 
hetucli c set amm_address <amm_pool_address>
hetucli amm pool-info
hetucli whetu approve --spender 0xa16E02E87b7454126E5E10d957A927A7F5B5d2be  --value 100 --sender test0
hetucli amm swap-hetu-for-alpha --hetu-amount-in  100 --alpha-amount-out-min 0   --sender test0 --to <to-address>
```

### WHETU

```bash
hetucli whetu deposit --sender <wallet_name> --value <amount>
hetucli whetu withdraw --sender <wallet_name> --amount <amount>
hetucli whetu balance-of <wallet_name_or_address>
hetucli whetu transfer --to <address> --value <amount> --sender <wallet_name>
hetucli whetu approve --spender <address> --value <amount> --sender <wallet_name>
hetucli whetu total-eth
hetucli whetu total-supply
hetucli whetu nonces --owner <address>
```

### Staking, Subnet, Swap

```bash
hetucli stake total-staked
hetucli stake add-stake --sender <wallet_name> --amount <amount>
hetucli subnet next-netuid
hetucli subnet regist --sender <wallet_name> --name <name> --description <description> --token-name <token_name> --token-symbol <token_symbol>
hetucli amm alpha-price
hetucli amm swap-hetu-for-alpha --sender <wallet_name> --hetu-amount-in <amount> --alpha-amount-out-min <amount> --to <address>
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
