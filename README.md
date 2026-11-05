# Rosé's Wine Shop

Rosé's Wine Shop is a web-based e-commerce application developed using Python Flask and MySQL. The project combines online wine shopping functionality with sales analytics, machine learning models, and an AI-powered FAQ chatbot.

## Project Overview

The application provides customers with an online shopping experience while offering administrative sales insights through an interactive analytics dashboard.

## Features

### E-commerce Website
- User registration and login
- Password hashing using bcrypt
- Product browsing
- Shopping cart management
- Checkout and order processing
- Order history
- Newsletter subscription
- Customer support, FAQs, privacy policy, and terms pages

### Sales Analytics Dashboard
Built using Streamlit, Pandas, NumPy, and Plotly.

Dashboard features include:
- Key performance indicators (KPIs)
- Total bottles sold and average selling price
- Sales analysis by region and state
- Sales analysis by wine type
- Sales trends over time
- Interactive filters
- Full sales data table

### Machine Learning
The dashboard includes regression and classification functionality.

**Regression models**
- Gradient Boosting Regressor
- XGBoost Regressor

**Classification model**
- XGBoost Classifier

The dashboard displays actual versus predicted results, model evaluation metrics, and a confusion matrix.

### AI-Powered FAQ Chatbot
The chatbot uses:
- LangChain
- Hugging Face embeddings (`all-MiniLM-L6-v2`)
- FAISS vector search
- A locally hosted GGUF language model through llama.cpp

It retrieves relevant FAQ information and uses it to generate responses to customer questions.

## Technology Stack

| Category | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Backend | Python, Flask |
| Database | MySQL |
| Data Analysis | Pandas, NumPy |
| Visualization | Streamlit, Plotly, Matplotlib |
| Forecasting | Prophet |
| Machine Learning | Scikit-learn, XGBoost |
| AI Chatbot | LangChain, Hugging Face, FAISS, llama.cpp |

## Project Structure

```text
smart_wine_shop/
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
├── templates/
│   ├── home.html
│   ├── shop.html
│   ├── login.html
│   ├── signin.html
│   └── ...
│
├── app.py
├── chatbot.py
├── wine_dashboard.py
├── build_faiss.py
├── build_index.py
├── generate_faiss_index.py
├── faq.txt
├── requirements.txt
└── README.md
```

## Requirements

Before running the project, install:

- Python 3.9 or later
- MySQL Server
- Git
- A modern web browser

Additional Python packages are required for the Flask application and AI chatbot.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/mahisaahu/smart_wine_shop.git
cd smart_wine_shop
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

Some additional packages imported by the application may need to be installed separately.

### 3. Configure MySQL

Install and start MySQL Server.

Create a database and configure the connection details in the application files.

The project uses the following database tables:

- `users`
- `products`
- `purchases`
- `sales`
- `payment_details`
- `newsletter_subscribers`

The analytics dashboard retrieves sales information by joining the `sales` and `products` tables.

**Note:** The original database and its SQL schema are not included in this repository. The database and required tables must be recreated locally before running the application.

### 4. Configure the AI chatbot

The chatbot requires:

- A generated FAISS vector index.
- The `all-MiniLM-L6-v2` embedding model.
- A compatible GGUF language model.
- The required LangChain and llama.cpp dependencies.

The FAISS index and GGUF model files are not included in the repository. They must be generated or obtained separately and configured using appropriate local paths.

### 5. Run the Flask application

```bash
python app.py
```

The application runs locally using Flask.

### 6. Run the Streamlit dashboard

```bash
streamlit run wine_dashboard.py
```

The dashboard connects to the MySQL database and displays sales analytics and machine learning results.

## Important Notes

- The project was originally developed and tested in a local Windows environment.
- Database credentials and local model paths require local configuration.
- The MySQL database and its schema are not included.
- FAISS index files and the local GGUF language model are not included.
- Some product images and other image assets have been omitted from this repository to reduce its size. Certain images may therefore not display.
- Payment functionality is intended for project demonstration and is not a production-ready payment gateway.

## Project Purpose

This project demonstrates the integration of web development, database management, data analytics, machine learning, and retrieval-based AI chatbot functionality in an e-commerce application.

## Author

**Mahima Sahu**

GitHub: [mahisaahu](https://github.com/mahisaahu)
