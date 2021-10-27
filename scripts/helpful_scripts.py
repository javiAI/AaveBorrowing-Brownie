from brownie import (
    accounts,
    network,
    config,
    # MockV3Aggregator,
    # VRFCoordinatorMock,
    # LinkToken,
    # Contract,
    # interface,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-alc"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "local", "ganache-local"]


def get_account(index=None, id=None):
    """[summary]

    Args:
        index ([type], optional): [description]. Defaults to None.
        id ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    # accounts[0]
    # accounts.add('env')
    # accounts.load('id')
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active()
        in LOCAL_BLOCKCHAIN_ENVIRONMENTS + FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None
