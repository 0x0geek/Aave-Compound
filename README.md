<div id="top"></div>

<!-- ABOUT THE PROJECT -->
## AAVE-COMPOUND APY MAXIMIZER

 
<p align="center">
  <img alt="Dark" src="https://user-images.githubusercontent.com/83681204/165184890-83cbef58-3beb-413e-ae17-42ec24207d8a.png" width="100%">
</p>

This Dapp allows users to compare the live deposit and borrow APYs for different tokens in the AAVE and Compound protocols.


### Built With

* [Solidity](https://docs.soliditylang.org/)
* [Brownie](https://eth-brownie.readthedocs.io)
* [React.js](https://reactjs.org/)
* [ethers.js](https://docs.ethers.io/v5/)
* [web3modal](https://github.com/Web3Modal/web3modal)
* [material ui](https://mui.com/getting-started/installation/)


<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
      <a href="#how-it-works">How it Works</a>
    </li>
    <li>
      <a href="#how-to-use">How to Use</a>
      <ul>
        <li><a href="#scripts">Scripts</a></li>
        <li><a href="#testing">Testing</a></li>
        <li><a href="#front-end">Front End</a></li>
      </ul>
    </li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

Please install or have installed the following:
* [nodejs and npm](https://nodejs.org/en/download/) 
* [python](https://www.python.org/downloads/)
* [MetaMask](https://chrome.google.com/webstore/detail/metamask/nkbihfbeogaeaoehlefnkodbefgpgknn) Chrome extension installed in your browser

### Installation

1. Installing Brownie: Brownie is a python framework for smart contracts development,testing and deployments. It's quit like [HardHat](https://hardhat.org) but it uses python for writing test and deployements scripts instead of javascript.
   Here is a simple way to install brownie.
   ```
    pip install --user pipx
    pipx ensurepath
    # restart your terminal
    pipx install eth-brownie
   ```
   Or if you can't get pipx to work, via pip (it's recommended to use pipx)
    ```
    pip install eth-brownie
    ```
   
2. Clone the repo:
   ```sh
   git clone https://github.com/Aymen1001/aave-compound-apy-maximizer.git
   cd aave-compound-apy-maximizer
   ```
3. Set your environment variables
   To be able to deploy to real testnets you need to add your PRIVATE_KEY (You can find your PRIVATE_KEY from your ethereum wallet like metamask) and the infura project Id (just create an infura account it's free) to the .env file:
   ```
   PRIVATE_KEY=<PRIVATE_KEY>
   WEB3_INFURA_PROJECT_ID=<< YOUR INFURA PROJECT ID >>
   ```
   You can choose to use ethereum testnets like rinkeby, Kovan or any other evm compatible testnet.
   You'll also need some eth in the testnet. You can get it into your wallet by using a public faucet. 


<p align="right">(<a href="#top">back to top</a>)</p>


<!-- Working EXAMPLES -->
## How it Works

The application uses the aave interface ILending and the CTokenInterface from compound which allows to deposit and withdraw funds, and also to get the live supply & borrow apys from the aave and compound protocol respectively.

The YieldMaximizer smart contract allows a user to create it's own crypto asset manager on top of the AAVE and Compound protocols, it uses the IERC20 interfaces so the contract can support all ERC20 tokens. When a user deposit an amount of given ERC20 the contract aiutomatically checks the protocol with the highest deposit apy and move the funds to it.

YieldMaximizer has the following functionnalities:

<ul>
  <li><b>Add tokens:</b> user can choose the best ERC20 tokens listed on aave & compound and add them to the contract watchlist</li>
  <li><b>Deposit & withdraw:</b> for depositing and withdrawing funds from the smart contract</li>
  <li><b>Rebalance:</b> To check the best protocol and switch funds to it </li>  
</ul>


<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## How to Use

### Scripts

   In the aave-compound-apy-maximizer folder you'll find a directory scripts, it contain all the python code for deploying your contracts and also some useful functions
   
   To run the yield maximizer on the DAI token (just an example, you can pick any other ERC20) run the commmand:
   ```sh
   brownie run scripts/asset_manager.py
   ```
   This will deposit to the protocol with the highest APY and wait a certain amount of time, then print the gain made.
   
   The reset.py file is used to remove all previous contracts deployments from build directory:
   ```sh
   brownie run scripts/reset.py
   ```
   
   The update_front_end.py is used to transfer all the smart contracts and interfaces data (abi,...) and addresses to the front end in the artifacts directory:
   ```sh
   brownie run scripts/update_front_end.py
   ```
   
   
 <p align="right">(<a href="#top">back to top</a>)</p>
  
 ### Testing

   In the aave-compound-apy-maximizer folder you'll find a directory tests, it contain all the python code used for testing the YieldMaximizer smart contract functionalities
   
   You can run all the tests by :
   ```sh
   brownie test
   ```
   Or you can test each function individualy:
   ```sh
   brownie test -k <function name>
   ```
   
<p align="right">(<a href="#top">back to top</a>)</p>
   
### Front-end
   
   The user interface of this application is build using React JS, it can be started by running: 
   ```sh
   cd front-end
   yarn
   yarn start
   ```
   It uses the following libraries:
      <ul>
        <li><b>Ethers.js:</b> used as interface between the UI and the deployed smart contract</li>
        <li><b>Web3modal:</b> for conecting to Metamask</li>
        <li><b>ipfs-http-client:</b> for connecting  and uploading files to IPFS </li>
        <li><b>@reduxjs/toolkit & redux-persist:</b> for managing the app states (account, balance, blockchain) </li>
        <li><b>Material UI:</b> used for react components and styles </li>    
      </ul>

   
<p align="right">(<a href="#top">back to top</a>)</p>


<!-- Contact -->
## Contact

If you have any question or problem running this project just contact me: aymenMir1001@gmail.com

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

