from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import subprocess
import re
import pymongo
import secrets



node_process = subprocess.Popen(['node', 'app.js'])
app=Flask(__name__)
app.secret_key = secrets.token_hex(16)
# Connect to the MongoDB database
client = pymongo.MongoClient('localhost', 27017)
db = client['mydb']
customers = db['customers']
class Customer:
    index = 0
    def __init__(self, name, vat, address):
        self.name = name
        self.vat = vat
        self.creation_date = datetime.now()
        self.address = address
        Customer.index += 1

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/customers', methods=['GET'])
def customer_list():
    customer_list = customers.find()
    return render_template('customers.html', customers=customer_list)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        vat = request.form['vat']
        #validation
        if not re.match(r'^[A-Z]{2}\d{10}$', vat):
            flash('Invalid VAT number. It should be two capital letters followed by 10 digits (e.g. PL1234567890)')
            return redirect(url_for('add_customer'))
        if not re.match(r'^[A-Za-z]+$',name):
            flash('Invalid name. It should be only letters upper or lower case or numbers (e.g. pl_ss)')
            return redirect(url_for('add_customer'))
        address = request.form['address']
        customer = Customer(name, vat, address)
        customers.insert_one(customer.__dict__)
        return redirect(url_for('customer_list'))
    return render_template('add_customer.html')

@app.route('/edit_customer/<string:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = customers.find_one({'_id': ObjectId(id)})
    if not customer:
        return redirect(url_for('customer_list'))


    if request.method == 'POST':
        name = request.form['name']
        vat = request.form['vat']
        if not re.match(r'^[A-Z]{2}\d{10}$', vat):
            flash('Invalid VAT number. It should be two capital letters followed by 10 digits (e.g. PL1234567890)')
            return redirect(url_for('add_customer'))
        if not re.match(r'^[A-Za-z0-9]+$',name):
            flash('Invalid name. It should be only letters upper or lower case or numbers (e.g. pl_ss)')
            return redirect(url_for('add_customer'))
        address = request.form['address']
        customers.update_one({'_id': ObjectId(id)}, {'$set': {'name': name, 'vat': vat, 'address': address}})
        return redirect(url_for('customer_list'))

    return render_template('edit_customer.html', customer=customer)

@app.route('/delete_customer/<string:id>', methods=['GET', 'POST'])
def delete_customer(id):
    if request.method == 'POST':
        customers.delete_one({"_id": ObjectId(id)})
        return redirect(url_for('customer_list'))
    customer = customers.find_one({"_id": ObjectId(id)})
    if not customer:
        return redirect(url_for('customer_list'))
    return render_template('delete_customer.html', customer=customer)
if __name__ == '__main__':
    app.run(debug=True)

node_process.terminate()