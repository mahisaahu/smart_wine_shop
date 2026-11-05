from flask import Flask, render_template, redirect, url_for, request, flash, session, make_response, Response, after_this_request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import bcrypt
from flask_mysqldb import MySQL
from functools import wraps
from datetime import datetime, timedelta
import pandas as pd
import joblib
from datetime import timedelta 
import socket
from llama_cpp import Llama
import subprocess
import signal  
import time
import socket

from flask import render_template
import joblib
import pandas as pd
from flask import jsonify
import numpy as np
from flask import request, jsonify
import requests as req  
import json
import re  

import subprocess
import os
from langchain_huggingface import HuggingFaceEmbeddings





app = Flask(__name__)

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_user'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'your_databse'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

# No-cache decorator
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        @after_this_request
        def add_header(response):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        return view(*args, **kwargs)
    return no_cache

# Forms
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

#-----------------------------------------------------------------

@app.route('/')
def home():
    return render_template('home.html')
# Newsletter subscription route
@app.route('/subscribe', methods=['POST'])
def subscribe_newsletter():
    email = request.form.get('email')
    if email:
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO newsletter_subscribers (email) VALUES (%s)', [email])
        mysql.connection.commit()
        cur.close()
        flash('Subscribed successfully! Thank you.', 'success')
    else:
        flash('Please enter a valid email.', 'warning')
    return redirect(url_for('home'))

#----------------------SHOPROUTE--------------------------------

@app.route('/shop')
@nocache
def shop():
    if 'user_id' not in session:
        flash("Please log in to access the shop.", "warning")
        return redirect(url_for('login', next=request.url))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, price, description, image_url, stock FROM products")
    products = cursor.fetchall()
    cursor.close()

    return render_template('shop.html', products=products, username=session.get('username'))

#-------------------------LOGINROUTE----------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
@nocache
def login():
    form = LoginForm()
    next_page = request.args.get('next')  # Capture 'next' from URL

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data.encode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password, user[3].encode('utf-8')):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash("Login successful!", "success")
            return redirect(next_page or url_for('shop'))  # Redirect to intended page
        else:
            flash("Login failed. Please check your email or password.", "danger")

    return render_template('login.html', form=form)


#---------------------------LOGOUTROUTE--------------------------------------------------

@app.route('/logout')
def logout():
    # Stop Streamlit if running
    streamlit_pid = session.get('streamlit_pid')
    if streamlit_pid:
        try:
            subprocess.run(["taskkill", "/PID", str(streamlit_pid), "/F", "/T"], check=True)
            print(f" Streamlit process {streamlit_pid} killed.")
        except Exception as e:
            print(f"Could not kill Streamlit process: {e}")

    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


#-----------------------------SIGNINROUTE----------------------------------------------------------



@app.route('/signin', methods=['GET', 'POST'])
@nocache
def signin():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already registered. Please log in.", "warning")
            cursor.close()
            return redirect(url_for('login'))

        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                       (name, email, hashed_password.decode('utf-8')))
        mysql.connection.commit()
        cursor.close()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signin.html', form=form)

#-----------------------------CARTROUTE------------------------------------------------


@app.route('/cart')
@nocache
def cart():
    if 'user_id' not in session:
        flash("Please log in to view your cart.", "warning")
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)


#----------------------------CHECKOUTROUTE----------------------------------------------

@app.route('/checkout', methods=['GET', 'POST'])
@nocache
def checkout():
    if 'user_id' not in session:
        flash("Please log in to checkout.", "warning")
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('cart'))

    total_price = sum(item['price'] * item['quantity'] for item in cart)

    if request.method == 'POST':
        # 🧾 Shipping details
        full_name = request.form.get('full_name')
        mobile = request.form.get('mobile')
        address1 = request.form.get('address1')
        address2 = request.form.get('address2') or ""
        pincode = request.form.get('pincode')
        country = request.form.get('country')
        state = request.form.get('state')
        region = request.form.get('region')
        payment_method = request.form.get('payment_method')
        purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Payment fields
        card_holder_name = request.form.get('card_name')
        card_number = request.form.get('card_number')
        expiry_date = request.form.get('card_expiry')
        cvv = request.form.get('card_cvv')
        upi_id = request.form.get('upi_id')

        # Combine full billing address
        billing_address = f"{full_name}, {mobile}, {address1}, {address2}, {pincode}, {region}, {state}, {country}"

        #  Hash card number and CVV
        card_number_hash = None
        cvv_hash = None
        if payment_method in ['Credit Card', 'Debit Card']:
            if card_number and cvv:
                card_number_hash = bcrypt.hashpw(card_number.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cvv_hash = bcrypt.hashpw(cvv.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        #  Save to `payment_details` table
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO payment_details (
                user_id, full_name, mobile, address1, address2, pincode,
                country, state, region, payment_method, upi_id,
                card_holder_name, card_number_hash, expiry_date,
                cvv_hash, billing_address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'], full_name, mobile, address1, address2, pincode,
            country, state, region, payment_method, upi_id,
            card_holder_name, card_number_hash, expiry_date,
            cvv_hash, billing_address
        ))

        # Check stock for all products
        for item in cart:
            cursor.execute("SELECT stock FROM products WHERE id = %s", (item['product_id'],))
            stock = cursor.fetchone()[0]
            if stock < item['quantity']:
                flash(f"Not enough stock for {item['name']}", "danger")
                cursor.close()
                return redirect(url_for('cart'))

        #  Record each item into `purchases` and `sales`
        for item in cart:
            item_total = item['price'] * item['quantity']

            # Insert into purchases
            cursor.execute("""
                INSERT INTO purchases (
                    user_id, product_id, product_name, price, quantity,
                    state, region, country, purchase_date, payment_method
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session['user_id'], item['product_id'], item['name'], item['price'], item['quantity'],
                state, region, country, purchase_date, payment_method
            ))

            # Update stock
            cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (item['quantity'], item['product_id']))

            # Insert into sales
            cursor.execute("""
                INSERT INTO sales (
                    product_id, quantity, price_per_unit, total_price,
                    buyer_id, payment_method, country, state, region, date_of_sale
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                item['product_id'], item['quantity'], item['price'], item_total,
                session['user_id'], payment_method, country, state, region
            ))

        mysql.connection.commit()
        cursor.close()
        session.pop('cart', None)
        flash("Order placed successfully!", "success")
        return redirect(url_for('shop'))

    return render_template('checkout.html', cart=cart, total_price=total_price)


#ORDERHITORY --------------------------------------------------------------------------
# order history
@app.route('/order_history')
@nocache
def order_history():
    if 'user_id' not in session:
        flash("Please log in to view your orders.", "warning")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT product_name, quantity, price, purchase_date, payment_method, country, state, region
        FROM purchases WHERE user_id = %s ORDER BY purchase_date DESC
    """, (session['user_id'],))
    orders = cursor.fetchall()
    cursor.close()
    return render_template('order_history.html', orders=orders)

#UPDATE CART ROUTE-------------------------------------------------------------



@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        flash("Please log in to add items to your cart.", "warning")
        return redirect(url_for('login'))

    product_id = request.form['product_id']
    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    item = {
        'product_id': product_id,
        'name': name,
        'price': price,
        'quantity': quantity
    }

    cart = session.get('cart', [])
    for existing in cart:
        if existing['product_id'] == product_id:
            existing['quantity'] += quantity
            break
    else:
        cart.append(item)

    session['cart'] = cart
    flash(f"{name} added to cart!", "success")
    return redirect(url_for('shop') + f"#{product_id}")

@app.route('/update_cart', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        flash("Please log in to update your cart.", "warning")
        return redirect(url_for('login'))

    product_id = request.form.get('product_id')
    action = request.form.get('action')

    if 'cart' in session and product_id:
        cart = session['cart']
        for item in cart:
            if item['product_id'] == product_id:
                if action == 'increase':
                    item['quantity'] += 1
                elif action == 'decrease' and item['quantity'] > 1:
                    item['quantity'] -= 1
                elif action == 'remove':
                    cart.remove(item)
                break
        session['cart'] = cart

    return redirect(url_for('cart'))

def is_port_in_use(port):
    """
    Check if a TCP port is open on localhost.
    Returns True if the port is in use, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@app.route('/dashboard')
@nocache
def streamlit_dashboard():
    if 'user_id' not in session:
        flash("Please log in to view the dashboard.", "warning")
        return redirect(url_for('login', next=request.path))

    if not is_port_in_use(8501):
        print("ℹ️ Starting Streamlit subprocess...")

        try:
            proc = subprocess.Popen(
                ["streamlit", "run", "wine_dashboard.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            session['streamlit_pid'] = proc.pid
            print(f"Streamlit started with PID {proc.pid}")

            time.sleep(3)

        except Exception as e:
            print(f" Failed to start Streamlit: {e}")
            flash("Could not start Streamlit dashboard.", "danger")
            return redirect(url_for('shop'))
    else:
        print(" Streamlit already running.")

    return redirect("http://localhost:8501")



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')
@app.route('/delivery')
def delivery():
    return render_template('delivery.html')


@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/discount')
def discount():
    return render_template('discount.html')




@app.context_processor
def inject_cart_count():
    cart = session.get('cart', [])
    total_items = sum(item.get('quantity', 1) for item in cart)
    return dict(cart_item_count=total_items)



from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)
from llama_cpp import Llama

llm = Llama(
    model_path="add_path",  #  Absolute path
        n_ctx=4096,
    n_threads=8,
    n_batch=256,
    verbose=False
)
print("Model loaded successfully!")
print(" Model info:", llm.model_path, "| Context size:", llm.n_ctx)
def get_bot_response(user_input):
    try:
        system_prompt = (
            "You are a helpful assistant at a wine store. "
            "Use the context below to answer the user's question. "
            "If the answer is not in the context, just say: 'I don't know.' "
            "Keep your answer concise and friendly."
        )

        # Retrieve similar documents from FAISS
        docs = vector_store.similarity_search(user_input, k=5)

        # Log retrieved context
        print(" Context docs retrieved:")
        for i, d in enumerate(docs, 1):
            print(f"\n--- Document {i} ---\n{d.page_content}")

        # Combine all retrieved texts
        context = "\n\n".join(doc.page_content for doc in docs)

        # Build prompt (formatted)
        prompt = f"""
### System Instructions:
{system_prompt}

### Context:
{context}

### User Question:
{user_input}

### Answer:
"""

        print(" Prompt:\n", prompt)

        # Model call
        response = llm(
            prompt=prompt,
            max_tokens=512,
            temperature=0.2,
            top_p=0.9,
         stop=["###"]
        )

        print("Raw Response:\n", response)

        output = response["choices"][0]["text"].strip()
        return output or "Sorry, I didn't get that. Could you rephrase?"

    except Exception as e:
        print("Error:", str(e))
        return "Oops! Something went wrong."






@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    print(" Received:", user_message)

    try:
        answer = get_bot_response(user_message)
        if not answer:
            answer = "Sorry, I didn't get that. Could you rephrase?"
        return jsonify({'response': answer})
    except Exception as e:
        print(" Error in chatbot route:", str(e))  # This line is crucial
        return jsonify({'response': "Oops! Something went wrong. Please try again later."})





@app.route('/faq_suggestions')
def faq_suggestions():
    questions = []
    with open("faq.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        match = re.match(r'Q:\s*(.+)', line.strip())
        if match:
            questions.append(match.group(1))
    return jsonify({"questions": questions})



@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        for item in cart:
            if int(item['product_id']) == product_id:
                cart.remove(item)
                break
        session['cart'] = cart
    flash("Item removed from cart.", "info")
    return redirect(url_for('cart'))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session:
        flash("Please log in to pay.", "warning")
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    if not cart:
        flash("Cart is empty.", "warning")
        return redirect(url_for('cart'))

    total_price = sum(item['price'] * item['quantity'] for item in cart)

    if request.method == 'POST':
        # Simulate successful payment
        return redirect(url_for('payment_success'))

    return render_template('payment.html', cart=cart, total_price=total_price)
@app.route('/test_llama')
def test_llama():
    prompt = (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n"
        "Explain what wine is.\n\n"
        "### Response:"
    )
    response = llm(
        prompt=prompt,
        max_tokens=128
    )
    return response["choices"][0]["text"].strip()




if __name__ == '__main__':
    app.run(debug=True)
