// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

//--------------------------------------------------------------------
// INTERFACES
import "../interfaces/IERC20.sol";

// Interface for Compound's cErc20 contract
interface CErc20 {
    function mint(uint256) external returns (uint256);

    function redeem(uint256) external returns (uint256);

    function supplyRatePerBlock() external returns (uint256);

    function balanceOf(address) external view returns (uint256);
}

// Interface for AAVE's aErc20 contract
interface AErc20 {
    function balanceOf(address) external view returns (uint256);
}

// Interface for AAVE's lending pool contract
interface ILendingPool {
    function deposit(
        address asset,
        uint256 amount,
        address onBehalfOf,
        uint16 referralCode
    ) external;

    function withdraw(
        address asset,
        uint256 amount,
        address to
    ) external;

    function getReserveData(address asset)
        external
        returns (
            uint256 configuration,
            uint128 liquidityIndex,
            uint128 variableBorrowIndex,
            uint128 currentLiquidityRate,
            uint128 currentVariableBorrowRate,
            uint128 currentStableBorrowRate,
            uint40 lastUpdateTimestamp,
            address aTokenAddress,
            address stableDebtTokenAddress,
            address variableDebtTokenAddress,
            address interestRateStrategyAddress,
            uint8 id
        );
}

contract YieldMaximizer {
    //--------------------------------------------------------------------
    // VARIABLES

    address public owner;

    ILendingPool iLendingPool;

    mapping(string => Token) public supportedERC20Tokens;
    string[] public supportedTokensSymbols;

    mapping(string => uint256) public userTokensAmountMapping;
    mapping(string => Protocol) public tokensProtocolMappings;

    struct Token {
        address erc20Address;
        address cErc20Address; // ctoken address
        address aErc20Address; // atoken address
    }

    enum Protocol {
        AAVE,
        COMPOUND
    }

    //--------------------------------------------------------------------
    // EVENTS

    event Deposit(address owner, uint256 amount, Protocol depositTo);
    event Withdraw(address owner, uint256 amount, Protocol withdrawFrom);
    event Rebalance(address owner, uint256 amount, Protocol depositTo);

    //--------------------------------------------------------------------
    // MODIFIERS

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    //--------------------------------------------------------------------
    // CONSTRUCTOR

    constructor(address _lendingPoolAddress) {
        owner = msg.sender;
        iLendingPool = ILendingPool(_lendingPoolAddress);
    }

    //--------------------------------------------------------------------
    // FUNCTIONS

    function addToken(
        string memory symbol,
        address _erc20Address,
        address _cErc20Address,
        address _aErc20Address
    ) public onlyOwner {
        supportedERC20Tokens[symbol] = Token(
            _erc20Address,
            _cErc20Address,
            _aErc20Address
        );
        supportedTokensSymbols.push(symbol);
    }

    function listSupportedTokens() public view returns (address[] memory) {
        string[] memory symbols = supportedTokensSymbols;
        address[] memory tokens = new address[](symbols.length);

        for (uint256 index = 0; index < symbols.length; index++) {
            tokens[index] = supportedERC20Tokens[symbols[index]].erc20Address;
        }
        return tokens;
    }

    function isSupportedToken(string memory _symbol)
        public
        view
        returns (bool)
    {
        if (supportedERC20Tokens[_symbol].erc20Address != address(0)) {
            return true;
        } else {
            return false;
        }
    }

    function deposit(
        uint256 _amount,
        string memory _symbol,
        uint256 _compAPY,
        uint256 _aaveAPY
    ) public {
        require(_amount > 0, "invalid amount");
        require(isSupportedToken(_symbol), "token not supported");

        Token memory _token = supportedERC20Tokens[_symbol];

        uint256 depositedAmount = userTokensAmountMapping[_symbol];

        IERC20(_token.erc20Address).transferFrom(
            msg.sender,
            address(this),
            _amount
        );
        userTokensAmountMapping[_symbol] += _amount;
        Protocol _currentProtocol;

        if (depositedAmount > 0) {
            _currentProtocol = tokensProtocolMappings[_symbol];
            if (_currentProtocol == Protocol.AAVE) {
                _depositToAave(_amount, _token.erc20Address);
            } else {
                _depositToCompound(
                    _amount,
                    _token.erc20Address,
                    _token.cErc20Address
                );
            }
        } else {
            if (_aaveAPY > _compAPY) {
                _depositToAave(_amount, _token.erc20Address);
                _currentProtocol = Protocol.AAVE;
            } else {
                _depositToCompound(
                    _amount,
                    _token.erc20Address,
                    _token.cErc20Address
                );
                _currentProtocol = Protocol.COMPOUND;
            }

            tokensProtocolMappings[_symbol] = _currentProtocol;
        }
        emit Deposit(msg.sender, _amount, _currentProtocol);
    }

    function withdraw(string memory _symbol) public onlyOwner {
        uint256 balance = userTokensAmountMapping[_symbol];
        Protocol _currentProtocol = tokensProtocolMappings[_symbol];
        Token memory _token = supportedERC20Tokens[_symbol];
        require(balance > 0);

        if (_currentProtocol == Protocol.COMPOUND) {
            require(_withdrawFromCompound(_token.cErc20Address) == 0);
        } else {
            _withdrawFromAave(_token.erc20Address, _token.aErc20Address);
        }
        userTokensAmountMapping[_symbol] = 0;

        balance = IERC20(_token.erc20Address).balanceOf(address(this));
        IERC20(_token.erc20Address).transfer(msg.sender, balance);

        emit Withdraw(msg.sender, balance, _currentProtocol);
    }

    function rebalance(
        string memory _symbol,
        uint256 _compAPY,
        uint256 _aaveAPY
    ) public onlyOwner {
        uint256 _amount = userTokensAmountMapping[_symbol];
        Protocol _currentProtocol = tokensProtocolMappings[_symbol];
        Token memory _token = supportedERC20Tokens[_symbol];

        require(_amount > 0);
        uint256 balance;

        if ((_compAPY > _aaveAPY) && (_currentProtocol != Protocol.COMPOUND)) {
            _withdrawFromAave(_token.erc20Address, _token.aErc20Address);

            balance = IERC20(_token.erc20Address).balanceOf(address(this));

            _depositToCompound(
                balance,
                _token.erc20Address,
                _token.cErc20Address
            );

            tokensProtocolMappings[_symbol] = Protocol.COMPOUND;

            emit Rebalance(msg.sender, _amount, Protocol.COMPOUND);
        } else if (
            (_aaveAPY > _compAPY) && (_currentProtocol != Protocol.AAVE)
        ) {
            _withdrawFromCompound(_token.cErc20Address);

            balance = IERC20(_token.erc20Address).balanceOf(address(this));

            _depositToAave(balance, _token.erc20Address);

            tokensProtocolMappings[_symbol] = Protocol.AAVE;

            emit Rebalance(msg.sender, _amount, Protocol.AAVE);
        }
    }

    function _depositToCompound(
        uint256 _amount,
        address _erc20Address,
        address _cErc20Address
    ) internal returns (uint256) {
        require(IERC20(_erc20Address).approve(_cErc20Address, _amount));
        uint256 result = CErc20(_cErc20Address).mint(_amount);
        return result;
    }

    function _withdrawFromCompound(address _cErc20Address)
        internal
        returns (uint256)
    {
        uint256 balance = CErc20(_cErc20Address).balanceOf(address(this));
        uint256 result = CErc20(_cErc20Address).redeem(balance);
        return result;
    }

    function _depositToAave(uint256 _amount, address _erc20Address) internal {
        require(IERC20(_erc20Address).approve(address(iLendingPool), _amount));
        iLendingPool.deposit(_erc20Address, _amount, address(this), 0);
    }

    function _withdrawFromAave(address _erc20Address, address _aErc20Address)
        internal
    {
        uint256 balance = AErc20(_aErc20Address).balanceOf(address(this));
        iLendingPool.withdraw(_erc20Address, balance, address(this));
    }

    function balanceOfContract(string memory _symbol)
        public
        view
        returns (uint256)
    {
        Protocol _currentProtocol = tokensProtocolMappings[_symbol];
        Token memory _token = supportedERC20Tokens[_symbol];
        if (_currentProtocol == Protocol.COMPOUND) {
            return CErc20(_token.cErc20Address).balanceOf(address(this));
        } else {
            return AErc20(_token.aErc20Address).balanceOf(address(this));
        }
    }

    function getCurrentProtocol(string memory _symbol)
        public
        view
        returns (Protocol)
    {
        return tokensProtocolMappings[_symbol];
    }
}
