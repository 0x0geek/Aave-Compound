import time
from brownie import interface, network, config, YieldMaximizer
from scripts.helper_scripts import (
    get_account, 
    toWei, 
    fromWei, 
    mint_erc20,
    approve_erc20, 
    get_erc20_balance, 
    FORKED_BLOCHCHAINS, 
)
from scripts.get_weth import get_weth

PROTOCOLS = {0: "AAVE", 1: "COMPOUND"}

def get_lending_pool():
    provider_address = config["networks"][network.show_active()]["provider"]
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(provider_address)
    lending_pool_address = lending_pool_address_provider.getLendingPool()

    print(lending_pool_address)
    lending_pool = interface.ILendingPool(lending_pool_address)

    return lending_pool

def get_compound_apy(ctoken):

    ctoken_contract = interface.CErc20(ctoken)
    supplyRate = ctoken_contract.supplyRatePerBlock.call()
    borrowRate = ctoken_contract.borrowRatePerBlock.call()

    eth_Mantissa =10 ** 18 
    blocks_per_Day = 6570
    days_in_Year = 365

    depositAPY = ((((supplyRate / eth_Mantissa * blocks_per_Day + 1) ** days_in_Year)) - 1) * 100

    borrowAPY = ((((borrowRate / eth_Mantissa * blocks_per_Day + 1) ** days_in_Year)) - 1) * 100

    print("compound deposit apy is: ", depositAPY)
    print("compound borrow apy is: ", borrowAPY)

    return toWei(depositAPY)

def get_aave_apy(token):

    LendingPool = get_lending_pool()
    data = LendingPool.getReserveData(token)

    RAY = 10**27 
    SECONDS_PER_YEAR = 31536000

    liquidityRate = data[3]
    variableBorrowRate = data[4]
    stableBorrowRate = data[5]

    depositAPR = liquidityRate / RAY
    variableBorrowAPR =  variableBorrowRate / RAY
    stableBorrowAPR =  stableBorrowRate / RAY

    depositAPY = ((1 + (depositAPR / SECONDS_PER_YEAR)) ** SECONDS_PER_YEAR) - 1

    variableBorrowAPY = ((1 + (variableBorrowAPR / SECONDS_PER_YEAR)) ** SECONDS_PER_YEAR) - 1
    stableBorrowAPY = ((1 + (stableBorrowAPR / SECONDS_PER_YEAR)) ** SECONDS_PER_YEAR) - 1

    print("aave weth apy is: ", depositAPY * 100)
    print("aave weth stable borrow apy is: ", stableBorrowAPY * 100)
    print("aave weth variable borrow apy is: ", variableBorrowAPY * 100)

    return toWei(depositAPY)

def main():

    dai_Token = config["networks"][network.show_active()]["dai-token"]
    cdai = config["networks"][network.show_active()]["cdai"]
    adai = config["networks"][network.show_active()]["adai"]

    account = get_account()

    if network.show_active() in FORKED_BLOCHCHAINS:
        get_weth(account, 30)
        mint_erc20(dai_Token, toWei(15), account)
    
    initial_erc20_balance = get_erc20_balance(dai_Token, account)

    lending_pool = get_lending_pool()

    maximizer = YieldMaximizer.deploy(lending_pool.address, {"from": account})

    add_token_tx = maximizer.addToken("DAI", dai_Token, cdai, adai, {"from": account})
    add_token_tx.wait(1)

    compAPY = get_compound_apy(cdai)
    aaveApy = get_aave_apy(dai_Token)

    amount = toWei(20000)

    approve_erc20(dai_Token, maximizer.address, amount, account)

    deposit_tx = maximizer.deposit(amount, "DAI", compAPY, aaveApy, {"from": account})

    deposit_tx.wait(1)

    current_protocol = maximizer.getCurrentProtocol("DAI")

    print("current protocol : ", PROTOCOLS[current_protocol])

    time.sleep(60)

    withdraw_tx = maximizer.withdraw("DAI", {"from": account})
    withdraw_tx.wait(1)

    final_erc20_balance = get_erc20_balance(dai_Token, account)

    print(f"Dai initial balance: {fromWei(initial_erc20_balance)} DAI")
    print(f"Dai final balance: {fromWei(final_erc20_balance)} DAI")

    difference = float(fromWei(final_erc20_balance)) - float(fromWei(initial_erc20_balance))
    print("yield gained: ", difference * 100)
    
    