from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
key = os.getenv('API_KEY')

def make_customer(firstName, lastName):
    url = f'http://api.nessieisreal.com/customers?key={key}'
    payload = {
        "first_name": firstName,
        "last_name": lastName,
        "address": {
            "street_number": '3333',
            "street_name": 'Walnut Street',
            "city": 'Philadelphia',
            "state": 'PA',
            "zip": '19104'
        }
    }
    headers = {'content-type':'application/json'}
    response = requests.post(
        url, 
        data=json.dumps(payload), 
        headers=headers
        )
    
    if response.status_code == 201:
        customer_id = response.json()['objectCreated']['_id']
        print('Customer ID: ' + customer_id)
        print('Customer created. Please save your customer id in a safe and secure environment immediately or your account will be lost forever')
        return customer_id
    else:
        print('Customer not created')



def make_account(id, balance):
    url = f'http://api.nessieisreal.com/customers/{id}/accounts?key={key}'
    payload = {
        "type": 'Credit Card', #options: credit card, savings, checking (only doing credit card for simplicity)
        "nickname": 'Card',
        "rewards": 0,
        "balance": balance,
    }
    headers = {'content-type':'application/json'}
    response = requests.post(
        url, 
        data=json.dumps(payload), 
        headers=headers
        )
    
    if response.status_code == 201:
        account_id = response.json()['objectCreated']['_id']
        print('Account ID: ' + account_id)
        print('Account created. Please save your account id in a safe and secure environment immediately or your account will be lost forever')
        return account_id
    else:
        print('Account not created')

def delete_data(type):
    url = f'http://api.nessieisreal.com/data'
    params = {
        'type':type,
        'key':key
    }
    headers = {'content-type':'application/json'}
    response = requests.delete(
        url,
        params=params,
        headers=headers
        )
    
    if response.status_code == 204:
        print('Delete successful')
    else:
        print('Failed')


# API integration
def create_bill(id, payee, nickname, payment_date, payment_amount):
    url = f'http://api.nessieisreal.com/accounts/{id}/bills?key={key}'
    payload = {
        "status": "pending",
        "payee": payee,
        "nickname": nickname,
        "payment_date": payment_date,
        "recurring_date": 1,
        "payment_amount": payment_amount
    }   
    headers = {'content-type':'application/json'}
    response = requests.post(
        url=url, 
        data=json.dumps(payload),
        headers=headers
    )
    return response.json()['objectCreated']['_id'] #returns bill ID

def create_deposit(id, transaction_date, amount):
    url = f'http://api.nessieisreal.com/accounts/{id}/deposits?key={key}'
    payload = {
        "medium": "balance",
        "transaction_date": transaction_date,
        "status": "pending",
        "description": "string",
        "amount": amount
    }   
    headers = {'content-type':'application/json'}
    response = requests.post(
        url=url, 
        data=json.dumps(payload),
        headers=headers
    )
    return response.json()['objectCreated']['_id'] #returns deposit ID

def create_withdrawal(id, transaction_date, amount):
    url = f'http://api.nessieisreal.com/accounts/{id}/withdrawals?key={key}'
    payload = {
        "medium": "balance",
        "transaction_date": transaction_date,
        "status": "pending",
        "amount": amount,
        "description": "string"
    }
    headers = {'content-type':'application/json'}
    response = requests.post(
        url=url, 
        data=json.dumps(payload),
        headers=headers
    )
    return response.json()['objectCreated']['_id'] #returns withdrawal ID

def get_all_accounts():
    url = f'http://api.nessieisreal.com/accounts?type=Credit%20Card&key={key}'
    headers = {'content-type':'application/json'}
    response = requests.get(
        url=url,
        headers=headers
    )
    return response.json()

def transfer(payer_id, payee_id, amount):
    url = f'http://api.nessieisreal.com/accounts/{payer_id}/transfers?key={key}'
    payload = {
        "medium": "balance",
        "payee_id": payee_id,
        "transaction_date": '2023-09-10',
        "status": 'completed',
        "description": "string",
        'amount': amount
    }
    headers = {'content-type':'application/json'}
    response = requests.post(
        url=url,
        data=json.dumps(payload),
        headers=headers
    )
    return response.json()['objectCreated']['_id']