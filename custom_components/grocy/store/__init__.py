'''Store clients'''

from .store_none import NoneStoreApiClient
from .store_rami_levy import RamiLevyStoreApiClient
from .store_my_supermarket import MySupermarketStoreApiClient
from .store_shufersal import ShufersalStoreApiClient


def get_store(store_name: str):
    ''' Create and return store client'''
    if store_name.lower() == RamiLevyStoreApiClient.name.lower():
        return RamiLevyStoreApiClient()
    elif store_name.lower() == ShufersalStoreApiClient.name.lower():
        return ShufersalStoreApiClient()
    elif store_name.lower() == MySupermarketStoreApiClient.name.lower():
        return MySupermarketStoreApiClient()
    else:
       return NoneStoreApiClient()
