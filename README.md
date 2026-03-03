# ⚡ Smart Electricity Analytics Dashboard

A full-stack machine learning powered web application that analyzes electricity consumption patterns, forecasts future usage, detects anomalies, and simulates potential savings using customizable slab-based billing logic.

🚀 **Live App:** https://smart-electricity-analytics.streamlit.app/

---

## 📌 Project Overview

Smart Electricity Analytics is an end-to-end data analytics and forecasting platform built using Streamlit and Scikit-learn.

The application allows users to:

- Upload electricity bills (PDF format)
- Automatically extract monthly consumption data
- Forecast future electricity usage
- Detect irregular usage patterns
- Estimate future bill amounts
- Simulate savings using a What-If reduction model
- Configure custom slab-based billing structures

---

## 🧠 Key Features

### 🔐 Authentication System
- Secure login and registration
- Password hashing using bcrypt
- SQLite-backed user management

### 📂 Automated PDF Parsing
- Extracts month, year, and units from structured electricity bills
- Currently optimized for Jaypee Power format

### 📊 Feature Engineering
- Lag features (lag_1, lag_2)
- 3-month rolling mean
- Seasonal encoding (sin/cos transformation)
- Trend indexing

### 🤖 Machine Learning Forecasting
- Model comparison:
  - Linear Regression
  - Random Forest Regressor
- TimeSeriesSplit cross-validation
- Hyperparameter tuning with RandomizedSearchCV
- Recursive multi-step forecasting (next 3 months)

### 🚨 Anomaly Detection
- Residual-based detection
- Threshold = 2 × standard deviation
- Highlights abnormal usage deviations

### 💰 Slab-Based Billing Engine
- Customizable energy slabs
- Fixed charges
- Sanctioned load handling
- Surcharge calculation

### 📈 What-If Simulation
- Simulate reduction in usage
- Estimate monthly savings
- Calculate potential annual savings

### 🎨 Modern UI
- Custom Streamlit theme
- Clean dashboard layout
- Forecast visualization
- Feature importance graphs

---

## 🛠 Tech Stack

- **Frontend:** Streamlit
- **Backend Logic:** Python
- **Machine Learning:** Scikit-learn
- **Data Processing:** Pandas, NumPy
- **Visualization:** Matplotlib
- **Database:** SQLite
- **Authentication:** bcrypt
- **PDF Parsing:** pdfplumber

---

## 🗂 Project Structure
```
smart-electricity-analytics/
│
├── app.py
├── forecasting.py
├── anomaly.py
├── feature_engineering.py
├── slab_engine.py
├── parser.py
├── auth.py
├── database.py
├── requirements.txt
└── .streamlit/config.toml
```

---

## ⚙️ How to Run Locally

1. Clone the repository:
   git clone https://github.com/pandav259/smart-electricity-analytics.git
   cd smart-electricity-analytics

2. Install dependencies:
   pip install -r requirements.txt

3. Run the application:
   streamlit run app.py

---

## 📈 Model Workflow

1. Feature Engineering
2. Time-Series Cross Validation
3. Model Comparison (LR vs RF)
4. Hyperparameter Optimization
5. Recursive Multi-Step Forecasting
6. Residual-Based Anomaly Detection

---

## 🚀 Future Improvements

- Support for multiple bill formats
- Cloud database integration (PostgreSQL)
- Real-time usage analytics
- Smart recommendation engine
- Energy efficiency scoring

---

## 👩‍💻 Author

Built with ❤️ by Ashmi Verma

---

## 📜 License

This project is open-source and available for educational and portfolio purposes.
