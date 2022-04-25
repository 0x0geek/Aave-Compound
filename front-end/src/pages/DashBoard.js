import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import { makeStyles, Container } from "@material-ui/core";

const provider = new ethers.providers.Web3Provider(window.ethereum, "any");


const useStyles = makeStyles((theme) => ({
    Container: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: theme.spacing(2)
    }
}))


function DashBoard() {

    const classes = useStyles()
    return (
        <div className={classes.Container}>

            <div>
                <h1>DashBoard</h1>
            </div>
        </div>
    )
}

export default DashBoard;