from dotenv import load_dotenv
import os
import requests
import json
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__, template_folder='templates', static_folder = 'static')

load_dotenv()
key = os.getenv('API_KEY')

#hashmap to map parents to children
parent_child_pairs = {}

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
        "type": 'Credit Card', #has to be capitalized and formatted in a specific way, consider multiple choice
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




@app.route('/')
def home_page():
    print("home test")
    return render_template('home.html')

@app.route('/create')
def create_page():
    print("create page test")
    return render_template('create.html')

@app.route('/create', methods=['POST'])
def create_post():
    print("create post test")
    parentFirst = request.form.get('parentFirst')
    parentLast= request.form.get('parentLast')
    childFirst = request.form.get('childFirst')
    childLast = request.form.get('childLast')

    print(f"Received for data - Parent: {parentFirst} {parentLast}, Child: {childFirst} {childLast}")

    # pcid = make_customer(parentFirst, parentLast) #parent customer id
    # ccid = make_customer(childFirst, childLast) #child customer id

    # paid = make_account(pcid, parentFirst, parentLast) #parent account id
    # caid = make_account(ccid, childFirst, childLast) #child account id

    # parent_child_pairs[paid] = caid
    # print("paid" + paid)
    # flash('Your parent account id is ' + paid + ", and your child account id is " + caid + " . Please save these somewhere safe or you will lose access to your account forever.")
    return render_template(
        'submit.html',
        parFir=parentFirst,
        parLst=parentLast,
        chldFir=childFirst,
        chldLst=childLast
    )

@app.route('/submit', methods=['GET'])
def submit_get():
    print("test submit")
    parentFirst = request.args.get('parFir')
    parentLast = request.args.get('parLst')
    childFirst = request.args.get('chldFir')
    childLast = request.args.get('chldLst')

    # Now you can use these variables in your /submit_get route
    pcid = make_customer(parentFirst, parentLast)  # parent customer id
    ccid = make_customer(childFirst, childLast)  # child customer id

    paid = make_account(pcid, 100)  # parent account id
    caid = make_account(ccid, 2)  # child account id

    parent_child_pairs[paid] = caid
    print("paid" + paid)
    flash('Your parent account id is ' + paid + ", and your child account id is " + caid + " . Please save these somewhere safe or you will lose access to your account forever.")

@app.route('/submit', methods=['POST'])
def submit_page():
    print("submit test")
    return render_template('submit.html')


@app.route('/login')
def login_page():
    print("login")
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    print("login post test")
    account_id = request.form.get('account_id')

    if account_id in parent_child_pairs:
        return redirect(url_for('parent_page'))
    elif account_id in parent_child_pairs.values():
        return redirect(url_for('child_page'))
    else: 
        flash('Login failed. Please check your account ID and try again.')
        return redirect(url_for('login'))

@app.route('/parent')
def parent_page():
    print("parent page test")
    return render_template('parent.html')

@app.route('/child')
def child_page():
    print("child page test")
    return render_template('child.html')


if __name__ == '__main__':
    app.run(debug=True)


