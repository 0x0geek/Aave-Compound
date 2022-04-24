import time, pytest
from brownie import network, config, YieldMaximizer
from scripts.helper_scripts import (
    get_account, 
    toWei, 
    mint_erc20,
    approve_erc20, 
    get_erc20_balance, 
    FORKED_BLOCHCHAINS, 
    ZERO_ADDRESS
)
from scripts.get_weth import get_weth
from scripts.asset_manager import (
    get_aave_apy,
    get_compound_apy,
    get_lending_pool
)


PROTOCOLS = {"AAVE": 0, "COMPOUND": 1}

def test_deploy():
    if network.show_active() not in FORKED_BLOCHCHAINS:
        pytest.skip() 

    owner = get_account()

    lending_pool = get_lending_pool()

    maximizer = YieldMaximizer.deploy(lending_pool.address, {"from": owner})

    assert maximizer.address != ZERO_ADDRESS
    assert maximizer.owner() == owner

def test_add_token():

    if network.show_active() not in FORKED_BLOCHCHAINS:
        pytest.skip() 

    owner = get_account()

    dai_Token = config["networks"][network.show_active()]["dai-token"]
    cdai = config["networks"][network.show_active()]["cdai"]
    adai = config["networks"][network.show_active()]["adai"]

    lending_pool = get_lending_pool()

    maximizer = YieldMaximizer.deploy(lending_pool.address, {"from": owner})

    add_token_tx = maximizer.addToken("DAI", dai_Token, cdai, adai, {"from": owner})
    add_token_tx.wait(1)

    supported_tokens = maximizer.listSupportedTokens()

    dai_addresses = maximizer.supportedERC20Tokens("DAI")

    assert len(supported_tokens) == 1
    assert supported_tokens[0] == dai_Token
    assert dai_addresses[0] == dai_Token
    assert dai_addresses[1] == cdai
    assert dai_addresses[2] == adai

def test_deposit_erc20():
    if network.show_active() not in FORKED_BLOCHCHAINS:
        pytest.skip() 

    owner = get_account()

    dai_Token = config["networks"][network.show_active()]["dai-token"]
    cdai = config["networks"][network.show_active()]["cdai"]
    adai = config["networks"][network.show_active()]["adai"]

    lending_pool = get_lending_pool()

    maximizer = YieldMaximizer.deploy(lending_pool.address, {"from": owner})

    add_token_tx = maximizer.addToken("DAI", dai_Token, cdai, adai, {"from": owner})
    add_token_tx.wait(1)

    # Getting some DAI
    if network.show_active() in FORKED_BLOCHCHAINS:
        get_weth(owner, 10)
        mint_erc20(dai_Token, toWei(5), owner)

    amount = toWei(5000) # 5000 DAI

    # approve fund transfer to YieldMaximizer
    approve_erc20(dai_Token, maximizer.address, amount, owner)

    compApy = get_compound_apy(cdai)
    aaveApy = get_aave_apy(dai_Token)

    deposit_tx = maximizer.deposit(amount, "DAI", compApy, aaveApy, {"from": owner})
    deposit_tx.wait(1)

    current_protocol = maximizer.getCurrentProtocol("DAI")

    assert current_protocol == PROTOCOLS["AAVE"] if aaveApy > compApy else PROTOCOLS["COMPOUND"]
    assert maximizer.userTokensAmountMapping("DAI") == amount

def test_add_to_deposited_amount():
    if network.show_active() not in FORKED_BLOCHCHAINS:
        pytest.skip() 

    owner = get_account()

    dai_Token = config["networks"][network.show_active()]["dai-token"]
    cdai = config["networks"][network.show_active()]["cdai"]
    adai = config["networks"][network.show_active()]["adai"]

    lending_pool = get_lending_pool()

    maximizer = YieldMaximizer.deploy(lending_pool.address, {"from": owner})

    add_token_tx = maximizer.addToken("DAI", dai_Token, cdai, adai, {"from": owner})
    add_token_tx.wait(1)

    # Getting some DAI
    if network.show_active() in FORKED_BLOCHCHAINS:
        get_weth(owner, 10)
        mint_erc20(dai_Token, toWei(5), owner)

    amount_1 = toWei(5000) # 5000 DAI

    # approve fund transfer to YieldMaximizer
    approve_erc20(dai_Token, maximizer.address, amount_1, owner)

    compApy = get_compound_apy(cdai)
    aaveApy = get_aave_apy(dai_Token)

    deposit_tx = maximizer.deposit(amount_1, "DAI", compApy, aaveApy, {"from": owner})
    deposit_tx.wait(1)

    amount_2 = toWei(1000)

    approve_erc20(dai_Token, maximizer.address, amount_2, owner)

    deposit_tx_2 = maximizer.deposit(amount_2, "DAI", compApy, aaveApy, {"from": owner})
    deposit_tx_2.wait(1)

    current_protocol = maximizer.getCurrentProtocol("DAI")

    assert current_protocol == PROTOCOLS["AAVE"] if aaveApy > compApy else PROTOCOLS["COMPOUND"]
    assert maximizer.userTokensAmountMapping("DAI") == amount_1 + amount_2

def test_rebalance():
    if network.show_active() not in FORKED_BLOCHCHAINS:
        pytest.skip() 

    owner = get_account()

    dai_Token = config["networks"][network.show_active()]["dai-token"]
    cdai = config["networks"][network.show_active()]["cdai"]
    adai = config["networks"][network.show_active()]["adai"]

    lending_pool = get_lending_pool()

    maximizer = YieldMaximizer.deploy(lending_pool.address, {"from": owner})

    add_token_tx = maximizer.addToken("DAI", dai_Token, cdai, adai, {"from": owner})
    add_token_tx.wait(1)

    # Getting some DAI
    if network.show_active() in FORKED_BLOCHCHAINS:
        get_weth(owner, 10)
        mint_erc20(dai_Token, toWei(5), owner)

    amount = toWei(5000) # 5000 DAI

    # approve fund transfer to YieldMaximizer
    approve_erc20(dai_Token, maximizer.address, amount, owner)

    # put AAVE apy less than COMPOUND apy to ensure that comp protocol is chosen 
    compApy = toWei(5)
    aaveApy = toWei(3)

    deposit_tx = maximizer.deposit(amount, "DAI", compApy, aaveApy, {"from": owner})
    deposit_tx.wait(1)

    current_protocol_1 = maximizer.getCurrentProtocol("DAI")

    # put AAVE apy greater than COMPOUND apy to verify if rebalance is working
    compApy = toWei(2)
    aaveApy = toWei(4)

    rebalance_tx = maximizer.rebalance("DAI", compApy, aaveApy, {"from": owner})
    rebalance_tx.wait(1)

    current_protocol_2 = maximizer.getCurrentProtocol("DAI")

    assert current_protocol_1 == PROTOCOLS["COMPOUND"]
    assert current_protocol_2 == PROTOCOLS["AAVE"]

def test_withdraw():
    if network.show_active() not in FORKED_BLOCHCHAINS:
        pytest.skip() 

    owner = get_account()

    dai_Token = config["networks"][network.show_active()]["dai-token"]
    cdai = config["networks"][network.show_active()]["cdai"]
    adai = config["networks"][network.show_active()]["adai"]

    lending_pool = get_lending_pool()

    maximizer = YieldMaximizer.deploy(lending_pool.address, {"from": owner})

    add_token_tx = maximizer.addToken("DAI", dai_Token, cdai, adai, {"from": owner})
    add_token_tx.wait(1)

    # Getting some DAI
    if network.show_active() in FORKED_BLOCHCHAINS:
        get_weth(owner, 10)
        mint_erc20(dai_Token, toWei(5), owner)

    initial_dai_balance = get_erc20_balance(dai_Token, owner)
    amount = toWei(5000) # 5000 DAI

    # approve fund transfer to YieldMaximizer
    approve_erc20(dai_Token, maximizer.address, amount, owner)

    compApy = get_compound_apy(cdai)
    aaveApy = get_aave_apy(dai_Token)

    deposit_tx = maximizer.deposit(amount, "DAI", compApy, aaveApy, {"from": owner})
    deposit_tx.wait(1)

    # wait for 120s to make sure some yield is generated
    time.sleep(120)

    withdraw_tx = maximizer.withdraw("DAI", {"from": owner})
    withdraw_tx.wait(1)

    final_dai_balance = get_erc20_balance(dai_Token, owner)

    assert maximizer.userTokensAmountMapping("DAI") == 0
    assert maximizer.balanceOfContract("DAI") == 0
    assert final_dai_balance > initial_dai_balance
