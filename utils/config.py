config = {
    'BASE_URL': 'https://www.nasdaq.com/symbol/',
    'SHARES_SUFFIX': '/historical',
    'TRADES_SUFFIX': '/insider-trades',
    'SHARES_FILENAME': 'D:\###PROJECTS\dot\shares.txt',
    'PAGE_SUFFIX': '?page=',
    'PAGE_COUNT_LIMIT_TO_PARSE': 10,
}

shares = [
    'CVX',
    'AAPL',
    'GOOG',
    'OPTT',
]

trades_mapping = {
    'trader': {
        'insider_name': '0',
        'relation': '1',
        'owner_type': '4',
    },
    'trade': {
        'last_date': '2',
        'transaction_type': '3',
        'shares_traded': '5',
        'last_price': '6',
        'shares_held': '7',
        'share': '8',
    },
}
