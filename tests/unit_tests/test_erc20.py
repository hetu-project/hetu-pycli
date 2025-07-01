import pytest
from web3 import Web3
from hetu_pycli.src.hetu.wrapper.erc20 import Erc20


@pytest.fixture
def dummy_abi():
    # Minimal ABI for testing
    return [
        {
            "inputs": [
                {"internalType": "address", "name": "account", "type": "address"}
            ],
            "name": "balanceOf",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "decimals",
            "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]


def test_erc20_init(dummy_abi):
    # Just test class instantiation (mock provider)
    provider = Web3.HTTPProvider("dummy_rpc_url")
    contract = Erc20(
        "0x0000000000000000000000000000000000000000", provider, dummy_abi
    )
    assert contract is not None
    assert hasattr(contract, "contract")
    assert hasattr(contract, "web3")
