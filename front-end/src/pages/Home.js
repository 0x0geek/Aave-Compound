import React, { useState, useEffect } from 'react';
import Main from "../components/Main"
import { ethers } from 'ethers';
import { Table } from '@material-ui/core';
import { useSelector } from "react-redux";
import { makeStyles, Container } from "@material-ui/core";

import ILendingPoolAddressesProvider from "../artifacts/interfaces/ILendingPoolAddressesProvider.json";
import ILendingPool from "../artifacts/interfaces/ILendingPool.json";
import CErc20 from "../artifacts/interfaces/CErc20.json"
import config from "../utils/brownie-config.json";
import { tokens } from '../utils/helper';


const provider = new ethers.providers.Web3Provider(window.ethereum, "any");


const useStyles = makeStyles((theme) => ({
    Container: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: theme.spacing(2)
    }
}))


function Home() {
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

    useEffect(() => {
        getApys()
    }, [data.network])


    return (
        <div className={classes.Container}>

            <div>
                <h1>APY Maximizer</h1>
            </div>

            <br />

            <Container>

                <Table hover>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Deposit APY</th>
                            <th>Variable Borrow APY</th>
                            <th>Stable Borrow APY</th>
                            <th>Deposit APY</th>
                            <th>Borrow APY</th>
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
            <br />
            <br />
        </div>

    )
}

export default Home