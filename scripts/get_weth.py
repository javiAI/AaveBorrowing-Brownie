from scripts.helpful_scripts import get_account
from brownie import interface, network, config


def main():
    get_weth()
    # receive_weth()


def get_weth(account=None):
    """Mints WETH by depositing ETH."""
    # ABI
    # Address
    if not account:
        account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.01 * 10 ** 18})
    tx.wait(1)
    print(f"Received 0.1 WETH")


def receive_weth():
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.withdraw(0.11 * 10 ** 18, {"from": account})
