import requests
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

class CryptoDataCollector:
    def __init__(self, url, token):
        self.url = url
        self.token = token

        self.target_coins = [
            'bitcoin', 'ethereum', 'binancecoin', 'solana', 'cardano',
            'polygon', 'chainlink', 'avalanche-2', 'polkadot', 'litecoin'
        ]

    def collect_crypto_data(self):
        endpoint = "coins/markets"

        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": self.token
        }

        params = {
            "vs_currency": "usd",
            "ids": ",".join(self.target_coins)
        }

        response = requests.get(self.url+endpoint, headers=headers, params=params)

        if response.status_code != 200:
            print(f"API request failed with status {response.status_code}: {response.text}")
            return None

        api_data = response.json()

        filtered_data = self._extract_essential_fields(api_data)

        if not self._validate_api_response(filtered_data):
            print("Errors encountered in collect data")
            return None

        structured_data = self._add_collection_metadata(filtered_data)

        return structured_data

    def _extract_essential_fields(self, api_data):
        essential_fields = [
            'id',
            'symbol', 
            'name',
            'current_price',
            'market_cap',
            'market_cap_rank',
            'total_volume',
            'price_change_24h',
            'price_change_percentage_24h',
            'last_updated'
        ]

        filtered_coins = []
        for coin in api_data:
            filtered_coin = {}
            for field in essential_fields:
                if field in coin:
                    filtered_coin[field] = coin[field]
                else:
                    filtered_coin[field] = None

            filtered_coins.append(filtered_coin)

        return filtered_coins

    def _validate_api_response(self, filtered_data):

        if type(filtered_data) == list:
            for coin in filtered_data:
                if coin['id'] not in self.target_coins:
                    print(f"Cannot find the coin: {coin['id']} in data collected")
                    return False
            return True
            
        else:
            print("The data type isn't list")
            return False

    def _add_collection_metadata(self, filtered_data):
        return {
            'collection_metadata': {
                'timestamp': datetime.now().isoformat(),
                'source': 'coingecko_api',
                'coins_collected': len(filtered_data),
                'target_coins': self.target_coins
            },
            'coin_data': filtered_data
        }