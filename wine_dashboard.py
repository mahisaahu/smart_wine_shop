from sqlalchemy import create_engine
import streamlit as st
import pandas as pd
import numpy as np
import mysql.connector
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from xgboost import XGBRegressor, XGBClassifier
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, accuracy_score, confusion_matrix
import plotly.graph_objects as go
import plotly.figure_factory as ff

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Rosé's Wine Shop - Sales Dashboard")

# --- MySQL connection ---
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='flaskuser',
        password='flaskpass123',
        database='mydatabase'
    )

# --- Fetch data from DB ---
def fetch_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id, s.product_id, p.name as product_name,
               s.region, s.state, s.country, s.quantity, s.total_price, s.date_of_sale
        FROM sales s
        JOIN products p ON s.product_id = p.id
    """)
    sales_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(sales_data)

# --- Load Data ---
df = fetch_data()

# --- Date formatting ---
if 'date_of_sale' in df.columns:
    df['date_of_sale'] = pd.to_datetime(df['date_of_sale'])

# --- Sidebar Filters ---
st.sidebar.header(" Filter Data")
selected_regions = st.sidebar.selectbox("Pick Region", options=["All"] + sorted(df["region"].unique()), index=0)
if selected_regions != "All":
    df = df[df["region"] == selected_regions]

# Add dummy 'state' if not in DB
if 'state' not in df.columns:
    df['state'] = df['region']  # temporary state for UI purposes

selected_states = st.sidebar.selectbox("Pick State", options=["All"] + sorted(df["state"].unique()), index=0)
if selected_states != "All":
    df = df[df["state"] == selected_states]

selected_winetypes = st.sidebar.selectbox("Pick Wine Type", options=["All"] + sorted(df["product_name"].unique()), index=0)
if selected_winetypes != "All":
    df = df[df["product_name"] == selected_winetypes]

# --- Date Range Filter ---
if 'date_of_sale' in df.columns:
    with st.sidebar.expander("🗓️ Date Range"):
        date_range = st.date_input("Select Date Range", [df['date_of_sale'].min(), df['date_of_sale'].max()])
        df = df[(df['date_of_sale'] >= pd.to_datetime(date_range[0])) & (df['date_of_sale'] <= pd.to_datetime(date_range[1]))]

# --- ML Task Selection ---
st.sidebar.markdown("---")
ml_task = st.sidebar.radio("Select ML Task", ["Regression", "Classification"])

# --- Encoding ---
le_region = LabelEncoder()
le_type = LabelEncoder()
le_state = LabelEncoder()

df['region_enc'] = le_region.fit_transform(df['region'])
df['product_name_enc'] = le_type.fit_transform(df['product_name'])
df['state_enc'] = le_state.fit_transform(df['state'])

# --- Classification Target (NEW COLUMN) ---
df['price_category'] = pd.cut(df['total_price'], bins=[1500, 2500, 4000, np.inf], 
                              labels=["Affordable", 'Mid-range', 'Premium'])
le_category = LabelEncoder()
df['price_category_enc'] = le_category.fit_transform(df['price_category'].astype(str))

# --- KPI Section ---
st.subheader("Key Performance Indicators")
total_bottles = df['quantity'].sum()
average_price = df['total_price'].mean()
total_sales = (df['quantity'] * df['total_price']).sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Bottles Sold", f"{total_bottles:,}")
k2.metric("Average Price/Bottle", f"₹{average_price:.2f}")
k3.metric("Total Revenue", f"₹{total_sales:,.2f}")

# --- REGRESSION ---
if ml_task == "Regression":
    model_choice = st.sidebar.selectbox("Choose Regression Model", ["Gradient Boosting", "XGBoost"])

    X = df[['region_enc', 'product_name_enc', 'state_enc', 'quantity']]
    y = df['total_price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor() if model_choice == "Gradient Boosting" else XGBRegressor()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    k4.metric("R² Score", f"{r2:.3f}")

    results_df = pd.DataFrame({'Actual Price': y_test.values, 'Predicted Price': y_pred}).reset_index(drop=True)
    st.subheader(" Actual vs Predicted Sales Table")
    st.dataframe(results_df, use_container_width=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=results_df['Actual Price'], mode='lines+markers', name='Actual'))
    fig.add_trace(go.Scatter(y=results_df['Predicted Price'], mode='lines+markers', name='Predicted'))
    fig.update_layout(title='Actual vs Predicted Price (Regression)', xaxis_title='Sample Index', yaxis_title='Price')
    st.plotly_chart(fig, use_container_width=True)


# --- CLASSIFICATION ---
elif ml_task == "Classification":
    model_choice = st.sidebar.selectbox("Choose Classification Model", ["XGBoost Classifier"])

    st.write("Class counts (filtered):")
    class_counts_df = df['price_category'].value_counts().reset_index()
    class_counts_df.columns = ['Category', 'Count']
    st.dataframe(class_counts_df, use_container_width=True)


    X_cls = df[['region_enc', 'product_name_enc', 'state_enc', 'quantity']]
    y_cls = df['price_category_enc']

    if len(np.unique(y_cls)) < 2:
        st.warning("⚠️ Not enough class diversity to train. Please broaden your filter.")
        k4.metric("Accuracy", "N/A")

    else:
        Xc_train, Xc_test, yc_train, yc_test = train_test_split(
            X_cls, y_cls, test_size=0.2, random_state=42, stratify=y_cls
        )

        if len(np.unique(yc_train)) < 2:
            st.error("❌ Training data contains only one class. Please broaden your filter.")
            k4.metric("Accuracy", "N/A")

        else:
            model = XGBClassifier()
            model.fit(Xc_train, yc_train)
            yc_pred = model.predict(Xc_test)
            accuracy = accuracy_score(yc_test, yc_pred)
            k4.metric("Accuracy", f"{accuracy * 100:.2f}%")

            # Inverse transform to get labels
            yc_pred_labels = le_category.inverse_transform(yc_pred)
            yc_actual_labels = le_category.inverse_transform(yc_test)

            # Results table
            results_df_cls = pd.DataFrame({
                "Actual Category": yc_actual_labels,
                "Predicted Category": yc_pred_labels
            })

            st.subheader("📄 Actual vs Predicted Categories (Classification)")
            st.dataframe(results_df_cls.reset_index(drop=True), use_container_width=True)

            # Correct vs Incorrect bar chart
            results_df_cls['Match'] = results_df_cls['Actual Category'] == results_df_cls['Predicted Category']
            match_counts = results_df_cls['Match'].value_counts().rename(index={True: "Correct", False: "Incorrect"}).reset_index()
            match_counts.columns = ["Result", "Count"]
            fig_cls = px.bar(match_counts, x="Result", y="Count", color="Result", title="Correct vs Incorrect Predictions")
            st.plotly_chart(fig_cls, use_container_width=True)

            # Confusion Matrix Heatmap
            cm = confusion_matrix(yc_actual_labels, yc_pred_labels, labels=le_category.classes_)
            labels = [str(label) for label in le_category.classes_]
            fig_cm = ff.create_annotated_heatmap(
                z=cm, x=labels, y=labels, colorscale="YlGnBu", showscale=True
            )
            fig_cm.update_layout(
                title_text="🔥 Confusion Matrix", xaxis_title="Predicted", yaxis_title="Actual"
            )

            st.subheader("🔥 Confusion Matrix Heatmap")
            st.plotly_chart(fig_cm, use_container_width=True)

# --- Full Data Table ---
st.subheader("📋 Full Sales Data")
st.dataframe(df, use_container_width=True)

# --- Visualizations ---
st.subheader("📊 Sales Visualizations")
c1, c2 = st.columns(2)
with c1:
    fig1 = px.bar(df, x="region", y="total_price", title="Sales by Region", color="region")
    st.plotly_chart(fig1, use_container_width=True)
with c2:
    fig2 = px.pie(df, names="product_name", values="total_price", title="Sales by Wine Type")
    st.plotly_chart(fig2, use_container_width=True)

fig3 = px.bar(df, x="state", y="total_price", title="Sales by State", color="state")
st.plotly_chart(fig3, use_container_width=True)

fig4 = px.line(df, x="date_of_sale", y="quantity", title="Sales Over Time")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("🌞 Sales Breakdown")
fig5 = px.sunburst(df, path=['region', 'product_name'], values='quantity',
                   title="Sales by Region and Wine Type", width=600, height=500)
st.plotly_chart(fig5, use_container_width=False)
