# -*- coding: utf-8 -*-
"""appyy.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HbgbhTjkxNK1N9XfffsmBz8wE9_lp2xh
"""
import pandas as pd
import numpy as np
import streamlit as st

# Try to import plotly and sklearn, handle import errors
try:
    import plotly.express as px
except ImportError as e:
    st.error(f"Plotly could not be imported: {e}")

try:
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
except ImportError as e:
    st.error(f"Scikit-learn could not be imported: {e}")

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense
    from tensorflow.keras.callbacks import EarlyStopping
except ImportError as e:
    st.error(f"TensorFlow could not be imported: {e}")

# Load the dataset
@st.cache
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

file_path = 'Food_Prices_Kenya.csv'
data = load_data(file_path)

# Data preprocessing
data = data.dropna(axis=1, how='all')
data = data.reset_index(drop=True)
data = data.drop(0)
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
data = data.ffill()
data['Price'] = pd.to_numeric(data['Price'], errors='coerce')
data['Usdprice'] = pd.to_numeric(data['Usdprice'], errors='coerce')
data['Amount Produced'] = pd.to_numeric(data['Amount Produced'], errors='coerce')
data['Annual Rainfall'] = pd.to_numeric(data['Annual Rainfall'], errors='coerce')
data['Annual Temperature'] = pd.to_numeric(data['Annual Temperature'], errors='coerce')
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
numeric_columns = data.select_dtypes(include=['number']).columns
data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mean())
data['Month'] = data['Date'].dt.month
data['Year'] = data['Date'].dt.year
data.drop(columns=['Date'], inplace=True)

# Feature selection
features = ['Month', 'Year', 'Regions', 'Annual Rainfall', 'Annual Temperature']
X = data[features]
y = data['Price']
X = pd.get_dummies(X, columns=['Regions'], drop_first=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

if 'tf' in locals():
    # Define the ANN model
    model = Sequential()
    model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    history = model.fit(X_train, y_train, validation_split=0.2, epochs=200, batch_size=32, callbacks=[early_stopping])

    # Model evaluation
    loss, mae = model.evaluate(X_test, y_test)
    st.write(f"Model Evaluation - MAE: {mae}")
    y_pred = model.predict(X_test)
    st.write(f"Mean Absolute Error: {mean_absolute_error(y_test, y_pred)}")
    st.write(f"Mean Squared Error: {mean_squared_error(y_test, y_pred)}")
    st.write(f"R-squared: {r2_score(y_test, y_pred)}")
else:
    st.warning("TensorFlow is not available. Model training and evaluation will be skipped.")

# Streamlit app
st.set_page_config(page_title="Maize Crop Price Prediction", layout="wide")
st.title("Maize Crop Price Prediction")
st.sidebar.header("Input Parameters")

# User inputs
region = st.sidebar.selectbox("Region", data['Regions'].unique())
year = st.sidebar.selectbox("Year", data['Year'].unique())
month = st.sidebar.selectbox("Month", data['Month'].unique())

# Prepare input data for prediction
input_data = pd.DataFrame({
    'Month': [month],
    'Year': [year],
    'Regions': [region],
    'Annual Rainfall': [data['Annual Rainfall'].mean()],  # Replace with actual data or user input
    'Annual Temperature': [data['Annual Temperature'].mean()]  # Replace with actual data or user input
})

input_data = pd.get_dummies(input_data, columns=['Regions'], drop_first=True)
for col in X.columns:
    if col not in input_data.columns:
        input_data[col] = 0

# Predict using the ANN model if available
if 'model' in locals():
    predicted_price = model.predict(input_data)[0][0]
    st.write(f"Predicted Maize Price: {predicted_price} KES")
else:
    st.warning("Prediction model is not available.")

# Data visualization using Plotly
if 'px' in locals():
    st.subheader("Historical Price Trends")
    price_trends = data.groupby(['Year', 'Month'])['Price'].mean().reset_index()
    fig = px.line(price_trends, x='Year', y='Price', title='Average Maize Price Over Years')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Plotly is not available for data visualization.")

# Additional Features
st.subheader("Additional Information")
with st.expander("See explanation"):
    st.write("""
        This application predicts the maize crop price based on historical data, 
        including production volumes, annual temperature, and rainfall for various regions in Kenya.
    """)





