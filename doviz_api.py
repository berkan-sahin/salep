#!/usr/bin/env python3
from typing import Tuple
import requests

request_url = "https://api.getgeoapi.com/api/v2/currency/convert"
base_currency = "TRY"

def get_exchange_rate(currency: str, api_key: str) -> Tuple[float, str]:
    """Queries the exchange rate between the Turkish Lira and the specified currency.

    Please keep in mind that the currency names are hard-coded and it is recommended to invoke this function with
    the three-letter code for the desired currency when possible.

    Args:
        currency (str): The Turkish name or three-letter code for the desired currency
        api_key (str): Key for the currency API

    Raises:
        InvalidCurrencyError: If the specified currency is not supported by the API

    Returns:
        Tuple[float, str]: The exchange rate and the three-letter code for the desired currency
    """

    currency = currency.upper()

    currency_names = {"DOLAR": "USD", 
                      "AVRO": "EUR", 
                      "EURO" : "EUR",
                      "POUND": "GBP",
                      "STERLIN": "GBP",
                      "RUBLE": "RUB",
                      "YUAN": "CNY",
                      "YEN": "JPY",
                      "MANAT": "AZN"}

    if currency in currency_names.keys():
        currency = currency_names[currency]

    parameters = {"api_key": api_key,
                  "from": currency,
                  "to": base_currency,
                  "format": "json"}        

    result = requests.get(request_url, params=parameters)
    
    if result.status_code != 200:
        raise InvalidCurrencyError
    else:
        return result.json()["rates"][base_currency]["rate"], currency

class InvalidCurrencyError(Exception):
    """When the specified currency is not found"""
    pass