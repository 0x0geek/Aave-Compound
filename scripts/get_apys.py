from brownie import interface, network, config

weth_Token = config["networks"][network.show_active()]["weth-token"]
dai_Token = config["networks"][network.show_active()]["dai-token"]
cDai = config["networks"][network.show_active()]["cdai"]



def get_lending_pool():
    provider_address = config["networks"][network.show_active()]["provider"]
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(provider_address)
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)

    return lending_pool

def get_compound_apy():

    ctoken_contract = interface.CErc20(cDai)

    supplyRate = ctoken_contract.supplyRatePerBlock.call()

    borrowRate = ctoken_contract.borrowRatePerBlock.call()

    eth_Mantissa =10 ** 18 
    blocks_per_Day = 6570
    days_in_Year = 365

    depositAPY = ((((supplyRate / eth_Mantissa * blocks_per_Day + 1) ** days_in_Year)) - 1) * 100

    borrowAPY = ((((borrowRate / eth_Mantissa * blocks_per_Day + 1) ** days_in_Year)) - 1) * 100

    print("compound deposit apy is: ", depositAPY)
    print("compound borrow apy is: ", borrowAPY)

    return depositAPY

def get_aave_apy():

    LendingPool = get_lending_pool()
    data = LendingPool.getReserveData(dai_Token)

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

    return depositAPY * 100



def main():

    compAPY = get_compound_apy()
    aaveApy = get_aave_apy()





