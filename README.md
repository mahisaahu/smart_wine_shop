# smart_wine_shop
A full-stack wine e-commerce web application built using Python Flask, MySQL, HTML, CSS, JavaScript and Bootstrap, featuring user authentication, shopping cart, payment options and an admin analytics dashboard.
# Rosé's Wine Shop

Rosé's Wine Shop is a full-stack e-commerce web application developed using Python Flask, MySQL, HTML, CSS, JavaScript, and Bootstrap.

The project was developed to provide an online shopping experience with features such as user authentication, product browsing, cart management, order processing, and payment options. It also includes an AI-powered FAQ chatbot and an analytics dashboard for monitoring sales.

## Features

### E-commerce functionality
- User registration and login
- Product browsing and product details
- Shopping cart management
- Checkout and order placement
- Order history
- Multiple payment options, including Card, UPI, and Cash on Delivery
- OTP verification
- Delivery and order management

### AI-powered chatbot
- FAQ-based customer support
- FAISS vector search for retrieving relevant information
- HuggingFace embeddings
- Local LLaMA model integration

### Sales analytics
- Interactive admin dashboard built with Streamlit
- Sales data visualization
- Sales forecasting and prediction components

## Technologies Used

| Area | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Backend | Python, Flask |
| Database | MySQL |
| Data Visualization | Streamlit, Plotly |
| Machine Learning | XGBoost |
| Chatbot | FAISS, HuggingFace, LLaMA |

## Project Structure

```text
smart_wine_shop/
│
├── app.py
├── chatbot.py
├── wine_dashboard.py
├── build_faiss.py
├── build_index.py
├── generate_faiss_index.py
│
├── templates/
│   └── HTML templates
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
├── faq.txt
└── requirements.txt
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/mahisaahu/smart_wine_shop.git
```

### 2. Navigate to the project directory

```bash
cd smart_wine_shop
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the database

Set up a MySQL database and configure the required database credentials using environment variables.

### 7. Run the application

```bash
python app.py
```

## Notes

- A MySQL database needs to be configured before running the application.
- Database credentials and secret keys should be configured locally and should not be committed to the repository.
- The FAISS index needs to be generated before using the chatbot.
- The local LLaMA model needs to be downloaded and configured separately.

## Developer

**Mahima Sahu**

GitHub: https://github.com/mahisaahu

---

This project was developed as part of my internship experience, combining full-stack web development, database management, AI-based customer support, and data analytics.
