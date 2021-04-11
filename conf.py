from datetime import datetime, timedelta

# --------------------CHANGE HERE------------------------------------------

SUBREDDITS = ["all"]
KEYWORDS = ['BTC', 'Bitcoin', 'ETH', 'Ethereum', 'Tether', 'USDT', 'Polkadot', 'DOT',
            'Ripple', 'XRP', 'Cardano', 'ADA', 'Chainlink', 'Litecoin', 'LTC',
            'Bitcoin Cash', 'BCH', 'Binance Coin', 'Binance', 'BNB', 'Stellar', 'XLM',
            'USD Coin', 'USDC', 'Uniswap', 'UNI', 'Aave', 'Dogecoin', 'DOGE', 'Bitcoin SV',
            'BSV', 'EOS', 'Monero', 'XMR', 'NEM', 'XEM', 'Tron', 'TRX', 'Tezos', 'XTZ', 'Theta',
            'Synthetix Network Token', 'Synthetix', 'SNX', 'Cosmos', 'VeChain',
            'SushiSwap', 'MKR', 'Dai', 'Neo', 'Crypto.com Coin', 'Crypto.com', 'CRO',
            'Solana', 'SOL', 'UMA', 'Huobi Token', 'HT', 'Binance USD',
            'BUSD', 'UNUS SE D LEO', 'LEO', 'FTX Token', 'FTT', 'IOTA', 'MIOTA',
            'CEL', 'Dash', 'DASH', 'Elrond', 'EGLD', 'Avalanche', 'AVAX', 'DefiChain', 'DFI',
            'Filecoin', 'FIL', 'ZCash', 'ZEC', 'The Graph', 'GRT', 'Yearn.Finance', 'YFI',
            'Kusama', 'KSM', 'Decred', 'DCR', 'Revain', 'REV', 'Ethereum Classic']

# -----------------------------------------------------------------------------------

BASE_URLS = {"posts": 'https://api.pushshift.io/reddit/submission/search/?size=1000',
             "comments": 'https://api.pushshift.io/reddit/comment/search/?size=1000'}
SCRAPE_SUBMISSION_COMMENTS = True
IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'gif', 'png']
