# Cryptocurrency Exporter
Simple cryptocurrency exporter written in Python to expose metrics. Cryptocurrencies could be converted to specified currency as USD, EUR, CZK, etc.
I recommend set a timer to **5 seconds or higher** because servers of **coinmarketcap.com** would be overloaded. Server running on port 9510. 

You can convert currencies to: *AUD, BRL, CAD, CHF, CLP, CNY, CZK, DKK, EUR, GBP, HKD, HUF, IDR, ILS, INR, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PKR, PLN, RUB, SEK, SGD, THB, TRY, TWD, ZAR*

## Usage
```
usage: crypto.py [-h] [-d] [-c CURRENCY] [-t TIMER]

Cryptocurrency Exporter

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug logging (default: False)
  -c CURRENCY, --currency CURRENCY
                        Set currency to convert (default: USD)
  -t TIMER, --timer TIMER
                        Scrape timing in seconds (default: 5)
```

## Examples

- Default currency (USD) and with debug mode
```
crypto.py -d 
```
- Convert to EUR and scrape every 2 seconds from server
```
crypto.py -c EUR -t 2
```

## Metrics

- Converted metric to prefered currency (USD) 
```
crypto_converted{btc="1.0",currency="USD",id="bitcoin",name="Bitcoin",rank="1",symbol="BTC"} 11819.8
```

- Value in percent to show exchange rate by time (1h, 24h and 7d)
```
crypto_percent{id="bitcoin",name="Bitcoin",rank="1",symbol="BTC",time="1h"} 0.54
```

- Value in unix timestamp format
```
crypto_last_update{id="bitcoin",name="Bitcoin",rank="1",symbol="BTC"} 1517173760.0
```

- Status of requesting for data 
```
exporter_requests{server="api.coinmarketcap.com",status="200"} 4.0
```
