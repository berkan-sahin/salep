#!/usr/bin/env python3
import requests

request_url = "https://api.getgeoapi.com/api/v2/currency/convert"
base_currency = "TRY"

def get_exchange_rate(currency: str, api_key: str) -> (float, str):
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