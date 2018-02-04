#!/usr/bin/env python

import time
import sys
import os
import argparse
import logging
import requests
import json
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# VARIABLES
LPORT = 9510
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
SRV = "api.coinmarketcap.com"
stats = {}

# ARGUMENTS
parser = argparse.ArgumentParser(description='Cryptocurrency Exporter', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-d', '--debug', action='store_true', default=False, help='Enable debug logging')
parser.add_argument('-c', '--currency', default='USD', help='Set currency to convert')
parser.add_argument('-t', '--timer', default=5, help='Scrape timing in seconds') 

# Try to connect
def exporter():
    db = {}

### GET CRYPTO

    try:
        logging.debug("Downloading data: %s" % SRV)
        prepare = requests.get('https://' + SRV + '/v1/ticker/?convert=' + args.currency, verify=False)
        if prepare.status_code in stats:
            stats.update({prepare.status_code: stats.get(prepare.status_code) + 1})
        else:
            stats.update({prepare.status_code: 1})
        result = json.loads(prepare.text)
        db.update({"crypto": result})
    except:
        logging.error("Unable to download data from {}, because server returned status: {}".format(SRV, prepare.status_code))

    db.update({"requests": stats})
###

    return db


class CustomCollector(object):
    def collect(self):
        # Requests data status 
        try:
            exporter_requests = CounterMetricFamily('exporter_requests', 'Exporter request status for getting data', labels=['server', 'status'])
            for key, val in get_data["requests"].items():
                exporter_requests.add_metric([SRV, str(key)], float(val))
            yield exporter_requests
        except:
            logging.error("No metrics (exporter stats)")
        
        # Cryptocurrency metrics
        try:
            crypto_converted = CounterMetricFamily('crypto_converted', 'Cryptocurrency to ' + args.currency, labels=['name', 'id', 'symbol', 'btc', 'currency', 'rank'])
            crypto_percent = CounterMetricFamily('crypto_percent', 'Cryptocurrency percent change by time', labels=['name', 'id', 'symbol', 'time', 'rank'])
            crypto_last_update = CounterMetricFamily('crypto_last_update', 'Cryptocurrency last update', labels=['name', 'id', 'symbol', 'rank'])
            
            for item in get_data["crypto"]:
                try:
                    crypto_converted.add_metric([item['name'], item['id'], item['symbol'], item['price_btc'], args.currency, item['rank']], float(item['price_' + args.currency.lower()]))
                except:
                    logging.debug("No metrics (converted)")
                
                try:
                    crypto_percent.add_metric([item['name'], item['id'], item['symbol'], "1h", item['rank']], float(item['percent_change_1h']))
                    crypto_percent.add_metric([item['name'], item['id'], item['symbol'], "24h", item['rank']], float(item['percent_change_24h']))
                    crypto_percent.add_metric([item['name'], item['id'], item['symbol'], "7d", item['rank']], float(item['percent_change_7d']))
                except:
                    logging.debug("No metrics (percent)")
                
                try:
                    crypto_last_update.add_metric([item['name'], item['id'], item['symbol'], item['rank']], float(item['last_updated']))
                except:
                    logging.debug("No metrics (last_update)")
            
            yield crypto_converted
            yield crypto_percent
            yield crypto_last_update
        except:
            logging.error("No metrics (cryptocurrencies)")


if __name__ == '__main__':
    args = parser.parse_args()
    
    ## LOGGING
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=FORMAT)
    
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.ERROR)
    logging.info('Server starting...')
    logging.debug('Debug mode enabled')
    
    # Start up the server to expose the metrics.
    start_http_server(LPORT)
    logging.info('Server listening on port: %s' % LPORT)
    # Generate some requests.
    get_data = exporter()
    REGISTRY.register(CustomCollector())
    try:
        while True:
            # Sleep to next scrape from server 
            time.sleep(args.timer)
            get_data = exporter()
    except KeyboardInterrupt:
        logging.info('Server has been stopped!')
    except:
        logging.fatal("Server has been unexpectedly stopped!")
