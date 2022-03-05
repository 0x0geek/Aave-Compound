import React, { useState, useEffect } from 'react';
import Main from "../components/Main"
import { ethers } from 'ethers';
import { Table } from '@material-ui/core';
import { useSelector } from "react-redux";
import { makeStyles, Container } from "@material-ui/core"
import axios from "axios"

import ILendingPoolAddressesProvider from "../artifacts/interfaces/ILendingPoolAddressesProvider.json";
import ILendingPool from "../artifacts/interfaces/ILendingPool.json";
import CErc20 from "../artifacts/interfaces/CErc20.json"
import config from "../brownie-config.json";
import dai from "../tokens-img/dai.png"
import aave from "../tokens-img/aave.png"
import usdt from "../tokens-img/usdt.png"
import usdc from "../tokens-img/usdc.png"
import link from "../tokens-img/link.png"
import yfi from "../tokens-img/yfi.jpg"
import zrx from "../tokens-img/zrx.png"
import eth from "../tokens-img/eth.png"
import wbtc from "../tokens-img/wbtc.jpg"
import uni from "../tokens-img/uni.jpg"
import bat from "../tokens-img/bat.png"


const provider = new ethers.providers.Web3Provider(window.ethereum, "any");

const daiToken = config["networks"]["mainnet-fork"]["dai-token"]
const cDai = config["networks"]["mainnet-fork"]["cdai"];

const aaveTokensListURL = "https://wispy-bird-88a7.uniswap.workers.dev/?url=http://tokenlist.aave.eth.link";
const compTokensListURL = "https://raw.githubusercontent.com/compound-finance/token-list/master/compound.tokenlist.json";

const tokens = [
    {
        img: dai,
        symbol: "DAI",
        address: daiToken,
        compAddress: cDai
    },
    {
        img: aave,
        symbol: "AAVE",
        address: "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        compAddress: "0xe65cdb6479bac1e22340e4e755fae7e509ecd06c"
    },
    {
        img: yfi,
        symbol: "YFI",
        address: "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
        compAddress: "0x80a2ae356fc9ef4305676f7a3e2ed04e12c33946"
    },
    {
        img: usdt,
        symbol: "USDT",
        address: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        compAddress: "0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9"
    },
    {
        img: usdc,
        symbol: "USDC",
        address: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        compAddress: "0x39AA39c021dfbaE8faC545936693aC917d5E7563"
    },
    {
        img: eth,
        symbol: "ETH",
        address: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        compAddress: "0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5"
    },
    {
        img: bat,
        symbol: "BAT",
        address: "0x0D8775F648430679A709E98d2b0Cb6250d2887EF",
        compAddress: "0x6C8c6b02E7b2BE14d4fA6022Dfd6d75921D90E4E"
    },
    {
        img: link,
        symbol: "LINK",
        address: "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        compAddress: "0xFAce851a4921ce59e912d19329929CE6da6EB0c7"
    },
    {
        img: uni,
        symbol: "UNI",
        address: "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        compAddress: "0x35A18000230DA775CAc24873d00Ff85BccdeD550"
    },
    {
        img: wbtc,
        symbol: "WBTC",
        address: "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        compAddress: "0xC11b1268C1A384e55C48c2391d8d480264A3A7F4"
    },
    {
        img: zrx,
        symbol: "ZRX",
        address: "0xE41d2489571d322189246DaFA5ebDe1F4699F498",
        compAddress: "0xB3319f5D18Bc0D84dD1b4825Dcde5d5f7266d407"
    },

]

const useStyles = makeStyles((theme) => ({
    Container: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: theme.spacing(2)
    }
}))


function Dashboerd() {
    const classes = useStyles()

    const data = useSelector((state) => state.blockchain.value)

    const [tokensData, setTokensData] = useState([])

    const getLendingAddress = async () => {
        const addressProvider = config["networks"]["mainnet-fork"]["provider"]
        const lendingProvider = new ethers.Contract(addressProvider, ILendingPoolAddressesProvider.abi, provider);

        const lendingPoolAddress = await lendingProvider.getLendingPool()

        return lendingPoolAddress;
    }

    const calculateAAVEApy = async (token) => {

        const lendingAddress = await Promise.all([getLendingAddress()])
        const LendingPool = new ethers.Contract(lendingAddress[0], ILendingPool.abi, provider);

        const data = await LendingPool.getReserveData(token)

        const RAY = 10 ** 27
        const SECONDS_PER_YEAR = 31536000

        const liquidityRate = data[3]
        const variableBorrowRate = data[4]
        const stableBorrowRate = data[5]

        const depositAPR = liquidityRate / RAY
        const variableBorrowAPR = variableBorrowRate / RAY
        const stableBorrowAPR = stableBorrowRate / RAY

        const depositAPY = (((1 + (depositAPR / SECONDS_PER_YEAR)) ** SECONDS_PER_YEAR) - 1) * 100

        const variableBorrowAPY = (((1 + (variableBorrowAPR / SECONDS_PER_YEAR)) ** SECONDS_PER_YEAR) - 1) * 100
        const stableBorrowAPY = (((1 + (stableBorrowAPR / SECONDS_PER_YEAR)) ** SECONDS_PER_YEAR) - 1) * 100

        return { depositAPY, variableBorrowAPY, stableBorrowAPY };
    }

    const calculateCompApy = async (token) => {
        const CToken = new ethers.Contract(token, CErc20.abi, provider);

        const supplyRate = await CToken.callStatic.supplyRatePerBlock()
        const borrowRate = await CToken.callStatic.borrowRatePerBlock()

        const eth_Mantissa = 10 ** 18
        const blocks_per_Day = 6570
        const days_in_Year = 365

        const depositAPY = ((((supplyRate / eth_Mantissa * blocks_per_Day + 1) ** days_in_Year)) - 1) * 100

        const borrowAPY = ((((borrowRate / eth_Mantissa * blocks_per_Day + 1) ** days_in_Year)) - 1) * 100

        return { depositAPY, borrowAPY }
    }

    const getApys = async () => {
        const items = await Promise.all(tokens.map(async (token) => {
            const compData = await calculateCompApy(token.compAddress)
            const aaveData = await calculateAAVEApy(token.address)

            let item = {
                img: token.img,
                symbol: token.symbol,
                comp: compData,
                aave: aaveData
            }
            return item;
        }))
        setTokensData(items)
    }

    const fetchData = async () => {
        const aaveAllTokens = await axios.get(aaveTokensListURL)
        const aaveSupportedTokens = aaveAllTokens.data.tokens.filter(t => !t.symbol.startsWith('a') && t.chainId == 1)

        const compAllTokens = await axios.get(compTokensListURL)
        const compSupportedTokens = compAllTokens.data.tokens.filter(t => t.symbol.startsWith('c') && t.chainId == 1)
        console.log(compSupportedTokens)
        console.log(aaveSupportedTokens)



    }

    useEffect(() => {
        getApys()
        fetchData()
    }, [data.network])


    return (
        <>
            <Main />
            <div className={classes.Container}>

                <div>
                    <h1>DashBoard</h1>
                </div>

                <br />

                <Container>

                    <Table hover>
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>aave deposit APY</th>
                                <th>aave variable Borrow APY</th>
                                <th>aave stable Borrow APY</th>
                                <th>comp deposit APY</th>
                                <th>comp borrow APY</th>
                                <th></th>

                            </tr>
                        </thead>
                        <tbody>
                            {tokensData.map((d, index) => {
                                return (
                                    <tr key={index}>
                                        <td><img src={d.img} width='20px' /> {d.symbol}</td>
                                        <td>{parseFloat(d.aave.depositAPY).toFixed(2)}%</td>
                                        <td>{parseFloat(d.aave.variableBorrowAPY).toFixed(2)}%</td>
                                        <td>{parseFloat(d.aave.stableBorrowAPY).toFixed(2)}%</td>
                                        <td>{parseFloat(d.comp.depositAPY).toFixed(2)}%</td>
                                        <td>{parseFloat(d.comp.borrowAPY).toFixed(2)}%</td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </Table>

                </Container>
            </div>
            <br />
            <br />
        </>

    )
}

export default Dashboerd