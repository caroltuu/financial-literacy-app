from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, redirect, url_for, session
import database
import apis
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import plotly.graph_objects as go
import yfinance as yf

app = Flask(__name__, template_folder='templates', static_folder = 'static')
app.secret_key = os.getenv('SECRET_KEY')

load_dotenv()
key = os.getenv('API_KEY')

current_parent_id = ''
current_child_id = ''

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/create')
def create_page():
    return render_template('create.html')

@app.route('/create', methods=['POST'])
def create_post():
    parentFirst = request.form.get('parentFirst')
    parentLast= request.form.get('parentLast')
    childFirst = request.form.get('childFirst')
    childLast = request.form.get('childLast')
    parentBalance = request.form.get('parentBalance')
    childBalance = request.form.get('childBalance')

    print(f"Received for data - Parent: {parentFirst} {parentLast}, Child: {childFirst} {childLast}")
    
    return redirect(url_for(
        'submit_page',
        parFir=parentFirst,
        parLst=parentLast,
        chldFir=childFirst,
        chldLst=childLast,
        parBal = parentBalance,
        chldBal = childBalance
        )
    )
    
@app.route('/submit', methods=['GET'])
def submit_page():
    parentFirst = request.args.get('parFir')
    parentLast = request.args.get('parLst')
    childFirst = request.args.get('chldFir')
    childLast = request.args.get('chldLst')
    parentBalance = int(request.args.get('parBal'))
    childBalance = int(request.args.get('chldBal'))

    pcid = apis.make_customer(parentFirst, parentLast)  # parent customer id
    ccid = apis.make_customer(childFirst, childLast)  # child customer id
    
    paid = apis.make_account(pcid, parentBalance)  # parent account id
    caid = apis.make_account(ccid, childBalance)  # child account id

    database.insert_account(paid, caid, parentBalance, childBalance)
    return render_template('submit.html', parent_id = paid, child_id = caid)

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    account_id = request.form.get('account_id')
    if database.is_parent_id(account_id):
        session['current_parent_id'] = account_id
        session['current_child_id'] = database.get_account_info(account_id)[1]
        print("curr child id")
        print(current_child_id)
        return redirect(url_for(
            'parent_post', 
            id=account_id
            ))
    elif database.is_child_id(account_id):
        session['current_parent_id'] = database.get_account_info(account_id)[0]
        session['current_child_id'] = account_id
        return redirect(url_for(
            'child_page',
            id=account_id
            ))
    else: 
        return redirect(url_for('login_page'))

@app.route('/parent', methods=['GET'])
def parent_page():
    account_id = request.args.get('id')
    parentBalance = database.get_account_info(account_id)[2]
    childBalance = database.get_account_info(account_id)[3]
    return render_template('parent.html', parentBalance=parentBalance, childBalance=childBalance)

@app.route('/parent', methods=['POST'])
def parent_post():
    current_parent_id = session.get('current_parent_id')
    current_child_id = session.get('current_child_id')
    action = request.form.get('action')
    amount = int(request.form.get('amount'))
    if action == "deposit":
        database.update_parent(current_parent_id, database.get_account_info(current_parent_id)[2]-amount)
        database.update_child(current_child_id, database.get_account_info(current_child_id)[3]+amount)
        return redirect(url_for('parent_page', id=current_parent_id))
    elif action == "withdraw":
        database.update_parent(current_parent_id, database.get_account_info(current_parent_id)[2]+amount)
        database.update_child(current_child_id, database.get_account_info(current_child_id)[3]-amount)
        return redirect(url_for('parent_page', id=current_parent_id))
    else:
        return "Invalid action"


@app.route('/child', methods=['GET'])
def child_page():
    account_id = request.args.get('id')
    childBalance = database.get_account_info(account_id)[3]
    return render_template('child.html', childBalance=childBalance)


@app.route('/process-ticker', methods=['POST'])
def process_ticker():
    ticker = request.form['ticker']
    period = int(request.form['period'])
    interval = request.form['interval']
    stocks = get_stocks(ticker, interval, period)
    fig = go.Figure(data=[go.Candlestick(x=stocks.index,
                open=stocks['Open'],
                high=stocks['High'],
                low=stocks['Low'],
                close=stocks['Close'])])
    fig.show()
    current_child_id = session.get('current_child_id')
    return render_template('child.html', data=stocks, childBalance=database.get_account_info(current_child_id)[3])


def convert_datetime(datetime):
    year = str(datetime.year)
    month = str(datetime.month)
    if len(month) == 1:
        month = '0' + month
    day = str(datetime.day)
    if len(day) == 1:
        day = '0' + day
    return year + '-' + month + '-' + day

def get_stocks(stock, interval, days):
    ticker = yf.Ticker(f"{stock}")
    date = datetime.now()
    start = convert_datetime(date - timedelta(days=days))
    end = convert_datetime(date)
    stocks = ticker.history(interval=interval, start=start, end=end)
    stocks["Date"] = stocks.index
    stocks = stocks.drop(['Volume', 'Dividends', 'Stock Splits', 'Capital Gains'], axis=1)
    return stocks

#asynchronous
def deduct_taxes():
    current_date = datetime.datetime.now().date()
    if current_date.day % 14 ==0:
        amount = database.get_account_info(current_child_id)[3]*0.08
        apis.transfer(current_child_id, current_parent_id, amount)

def accrue_interest():
    current_date = datetime.datetime.now().date()
    if current_date.day % 14 ==0:
        amount = database.get_account_info(current_child_id)[3]*0.04
        apis.transfer(current_child_id, current_parent_id, amount)

scheduler = BackgroundScheduler()
scheduler.add_job(deduct_taxes, 'interval', minutes=60)
scheduler.start()


if __name__ == '__main__':
    database.create_table()
    app.run(debug=True)
