from web3 import Web3

class Weights:
    def __init__(self, contract_address, provider, abi):
        self.contract_address = contract_address
        self.web3 = Web3(provider)
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)

    def setWeights(self, netuid, newWeights):
        """
        Call setWeights(netuid, newWeights)
        :param netuid: uint16 (solidity name: 'netuid')
        :param newWeights: Weight[] (solidity name: 'newWeights')
        :return: []
        """
        return self.contract.functions.setWeights(netuid, newWeights).call()

    def weights(self, netuid, validator, dest):
        """
        Call weights(netuid, validator, dest)
        :param netuid: uint16 (solidity name: 'netuid')
        :param validator: address (solidity name: 'validator')
        :param dest: address (solidity name: 'dest')
        :return: [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}]
        """
        return self.contract.functions.weights(netuid, validator, dest).call() 