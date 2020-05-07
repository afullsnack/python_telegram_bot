import requests
from pprint import pprint

SPOT_URL = 'https://api.coinbase.com/v2/prices/{}/spot'
def get_spot(pair):
   try:
      res = requests.get(SPOT_URL.format(pair))
      res = res.json()
      return res['data']['amount']
   except Exception as e:
      print("there was an error: ", e)