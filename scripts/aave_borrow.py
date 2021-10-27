from brownie import network, interface, config
from scripts.helpful_scripts import (
    get_account,
    FORKED_LOCAL_ENVIRONMENTS,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
amount = Web3.toWei(0.01, "ether")
# amount= 100000000000000000


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    weth = interface.IWeth(erc20_address)
    if weth.balanceOf(account.address) <= 0.1 * 10 ** 18:
        print("Getting some Weth")
        get_weth(account)
    else:
        print("You have enough balance of Weth. Not swapping ETH for WETH.")
    print("Balance:", weth.balanceOf(account.address) / 10 ** 18, "WETH")
    # ABI
    # address
    lending_pool = get_lending_pool()
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow!")
    # DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # borrowable_eth -> borrowable_dai * 0.95
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # Now we will borrow
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        amount_dai_to_borrow,
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI!")
    get_borrowable_data(lending_pool, account)
    repay_all(amount, lending_pool, account)
    print("You just deposited, borrowed and repayed with Aave, Brownie and Chainlink!")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repayed!")


def get_asset_price(price_feed_addres):
    # ABI
    # Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_addres)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH latest price is {converted_latest_price}")
    return float(converted_latest_price)


def get_borrowable_data(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowETH,
        currentLiquidiationThreshold,
        LTV,
        healthFactor,
    ) = lending_pool.getUserAccountData(account.address)

    totalCollateralETH = Web3.toWei(totalCollateralETH, "ether")
    totalDebtETH = Web3.toWei(totalDebtETH, "ether")
    availableBorrowETH = Web3.toWei(availableBorrowETH, "ether")
    print(f"You have {totalCollateralETH} worth of ETH deposited.")
    print(f"You have {totalDebtETH} worth of ETH borrowed.")
    print(f"You have {availableBorrowETH} worth of ETH deposited.")
    return (float(availableBorrowETH), float(totalDebtETH))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    # ABI (interface)
    # address
    erc20 = interface.IERC20(erc20_address)

    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    # Approve sending out ERC20 token
    # approve_erce20()
    return lending_pool
