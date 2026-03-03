import parser
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from database import create_tables
from auth import register_user, login_user
from feature_engineering import prepare_features
from forecasting import train_models, recursive_forecast
from anomaly import detect_anomalies
from slab_engine import (
    get_slabs,
    get_billing_settings,
    bill_exists,
    save_bill,
    get_all_bills,
    calculate_bill,
    save_slabs,
    save_billing_settings
)

create_tables()

# -----------------------
# Session Initialization
# -----------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

st.title("⚡ Smart Electricity Analytics")

# -----------------------
# If NOT Logged In
# -----------------------
if st.session_state.user_id is None and not st.session_state.demo_mode:

    st.markdown("## Welcome to Smart Electricity Analytics")
    st.caption("AI-powered electricity usage forecasting & bill optimization")

    st.markdown(
        """
        ### What you can do:
        - 📈 Predict next month's electricity consumption  
        - ⚠ Identify unusual usage spikes  
        - 💰 Estimate upcoming bills  
        - 🔎 Understand seasonal patterns  
        """
    )

    st.markdown("### Explore Without Login")   
    if st.button("🚀 Try Demo Mode"):
        st.session_state.demo_mode = True
        st.rerun()

    st.write("Login or create an account to continue.")

    tab_login, tab_signup = st.tabs(["Login", "Get Started"])

    # -----------------------
    # LOGIN TAB
    # -----------------------
    with tab_login:
        st.subheader("Login")

        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_btn"):
            user_id = login_user(username, password)

            if user_id:
                st.session_state.user_id = user_id
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    # -----------------------
    # SIGN UP TAB
    # -----------------------
    with tab_signup:
        st.subheader("Sign up to create an account:")

        new_username = st.text_input("Choose Username", key="signup_user")
        new_password = st.text_input("Choose Password", type="password", key="signup_pass")

        if st.button("Register", key="register_btn"):

                if len(new_username.strip()) == 0:
                    st.error("Username cannot be empty.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success = register_user(new_username, new_password)

                    if success:
                        st.success("Account created successfully! Please login.")
                        st.session_state.active_tab = "Login"
                    else:
                        st.error("Username already exists.")

    st.caption("🔒 Your data is securely stored and encrypted.")


# -----------------------
# If Logged In
# -----------------------
else:
    st.success("You are logged in! 🎉")

    existing_slabs = get_slabs(st.session_state.user_id)
    existing_settings = get_billing_settings(st.session_state.user_id)

    with st.sidebar:
        st.header("⚙️ CONFIGURATION")
        st.subheader("⚡ SLABS")

        if existing_slabs:
            num_slabs = len(existing_slabs)
        else:
            num_slabs = 3

        num_slabs = st.number_input(
            "Number of Slabs",
            min_value=1,
            max_value=5,
            value=num_slabs
        )

        slabs = []

        for i in range(num_slabs):
            st.write(f"Slab {i+1}")

            if existing_slabs and i < len(existing_slabs):
                default_min, default_max, default_rate = existing_slabs[i]
            else:
                # Jaypee default template
                if i == 0:
                    default_min, default_max, default_rate = 0, 150, 5.5
                elif i == 1:
                    default_min, default_max, default_rate = 151, 300, 6.0
                else:
                    default_min, default_max, default_rate = 301, 9999, 6.5

            min_units = st.number_input(
                f"Minimun Units",
                min_value=0,
                step=1,
                value=int(default_min),
                key=f"min_{i}"
            )
            max_units = st.number_input(
                f"Maximum Units",
                min_value=0,
                step=1,
                value=int(default_max),
                key=f"max_{i}"
            )
            rate = st.number_input(
                f"Rate per Unit",
                min_value=0.0,
                step=0.1,
                value=float(default_rate),
                key=f"rate_{i}"
            )
            slabs.append({
                "min": min_units,
                "max": max_units,
                "rate": rate
            })

        st.subheader("BILLING SETTINGS")

        if existing_settings:
            default_fixed, default_load, default_surcharge = existing_settings
        else:
            default_fixed = 110.0
            default_load = 8.0
            default_surcharge = 5.0

        fixed_charge = st.number_input(
            "Fixed Charge per kW",
            value=float(default_fixed)
        )
        sanctioned_load = st.number_input(
            "Sanctioned Load (kW)",
            value=float(default_load)
        )
        surcharge = st.number_input(
            "Surcharge (%)",
            value=float(default_surcharge)
        )

        if st.button("Save Configuration"):

            save_slabs(st.session_state.user_id, slabs)
            save_billing_settings(st.session_state.user_id, fixed_charge, sanctioned_load, surcharge)

            st.success("Configuration saved successfully!")

        if st.button("Logout"):
            st.session_state.user_id = None
            st.rerun()

        if st.session_state.demo_mode:
            st.markdown("---")
            if st.button("Exit Demo Mode"):
                st.session_state.demo_mode = False
                st.rerun()


    with st.expander("📂 Stored Bills", expanded=False):

        if st.session_state.demo_mode:
            bills_df = pd.DataFrame({
                "month": list(range(1, 13)),
                "year": [2024] * 12,
                "units": [239.2, 221.35, 229.94, 310.65, 370.21, 388.14, 370.59, 439.54, 324.66, 319.51, 234.6, 213.05],
                "energy": [0]*12,
                "fixed": [0]*12,
                "ed": [0]*12,
                "total": [2352.21, 2239.75, 2293.87, 2807.94, 3214.44, 3336.81, 3217.03, 3687.61, 2903.55, 2868.41, 2323.23, 2187.47]
            })
        else:
            rows = get_all_bills(st.session_state.user_id)
            if rows:
                bills_df = pd.DataFrame(rows, columns=[
                    "month", "year",
                    "units",
                    "energy",
                    "fixed",
                    "ed",
                    "total"
                ])
            else:
                bills_df = pd.DataFrame()

        if not bills_df.empty:

            bills_df["month"] = bills_df["month"].astype(int)
            bills_df["year"] = bills_df["year"].astype(int)

            bills_df["date"] = pd.to_datetime(
                dict(
                    year=bills_df["year"],
                    month=bills_df["month"],
                    day=1
                )
            )

            bills_df["month_year"] = (
                bills_df["month"].astype(str) + "/" +
                bills_df["year"].astype(str)
            )

            st.dataframe(
                bills_df[["month_year", "units", "total"]],
                use_container_width=True
            )

        else:
            st.info("No bills uploaded yet.")

    if "uploader_version" not in st.session_state:
        st.session_state.uploader_version = 0

    
    st.subheader("📥 Upload Monthly Bills")
    st.caption("Upload multiple electricity invoices to automatically extract and store usage data.")

    uploaded_files = st.file_uploader(
        "Select PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"bill_uploader_{st.session_state.uploader_version}"
    )

    if uploaded_files:

        new_bills = 0
        skipped_bills = 0
        failed_bills = 0

        for uploaded_file in uploaded_files:

            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.read())
            parsed_data = parser.parse_jaypee_bill(uploaded_file.name)

            if not parsed_data or not parsed_data.get("month"):
                failed_bills += 1
                continue

            month = parsed_data["month"]
            year = parsed_data["year"]
            exists = bill_exists(
                st.session_state.user_id,
                month,
                year
            )

            if exists:
                skipped_bills += 1
            else:
                save_bill(
                    st.session_state.user_id,
                    parsed_data,
                    replace=False
                )
                new_bills += 1

        if new_bills > 0:
            st.success(f"✅ {new_bills} bill(s) added successfully.")
            st.session_state.uploader_version += 1
            st.rerun()

        if skipped_bills > 0 and new_bills == 0:
            st.warning(f"⚠ {skipped_bills} duplicate bill(s) skipped.")

        if failed_bills > 0:
            st.error(f"❌ {failed_bills} file(s) could not be processed.")


    # -----------------------
    # 📊 Historical Data Section
    # -----------------------

    if not bills_df.empty:
        df = pd.DataFrame(bills_df, columns=[
            "month", "year",
            "units",
            "energy",
            "fixed",
            "ed",
            "total"
        ])

        df["date"] = pd.to_datetime(
            dict(
                year=df["year"].astype(int),
                month=df["month"].astype(int),
                day=1
            )
        )

        df = df.sort_values("date")

        # -----------------------
        # ⏳ Detect Large Gaps Between Months
        # -----------------------

        df["month_gap"] = (
            (df["date"].dt.year - df["date"].shift().dt.year) * 12 +
            (df["date"].dt.month - df["date"].shift().dt.month)
        )

        max_gap = df["month_gap"].iloc[1:].max()

        if max_gap and max_gap > 3:
            st.warning(
                f"⚠ Large gap detected between bills (max gap ≈ {round(max_gap, 1)} months). "
                "Forecast accuracy may be reduced."
            )


        # -----------------------
        # 🧠 Feature Engineering
        # -----------------------
        df_model = prepare_features(df)

        if len(df_model) < 6:
            st.warning(
                "📈 Not enough historical data for reliable forecasting.\n\n"
                "For accurate predictions, please upload at least 8–10 months "
                "of continuous billing data."
            )
            st.info(
                "Forecasting uses lag features and rolling averages, which require "
                "sufficient historical continuity."
            )            
            st.stop()

        # -----------------------
        # 🎯 Prepare ML Data
        # -----------------------
        feature_cols = [
            "lag_1",
            "lag_2",
            "rolling_mean_3",
            "month_sin",
            "month_cos",
            "trend_index"
        ]
        X = df_model[feature_cols]
        y = df_model["units"]

        # -----------------------
        # 🤖 Model Training
        # -----------------------
        rf_final, comparison_df, best_params = train_models(X, y)


        # -----------------------
        # 🔍 Feature Importance Df & Graph
        # -----------------------
        importances = rf_final.feature_importances_
        importance_df = pd.DataFrame({
            "feature": feature_cols,
            "importance": importances
        }).sort_values("importance", ascending=False)


        # -----------------------
        # 🚨 Anomaly Detection
        # -----------------------
        df_model, anomalies = detect_anomalies(rf_final, X, df_model)
        

        # -----------------------
        # 🔮 Recursive Forecast (Next 3 Months)
        # -----------------------
        forecast_df, future_predictions = recursive_forecast(
            rf_final,
            df_model,
            forecast_steps=3
        )

        # -----------------------
        # 💰 Forecast Bill Amount
        # -----------------------
        forecast_totals = []

        if slabs:

            slab_list = slabs
            surcharge_percent = surcharge

            for units in future_predictions:
                total_amount = calculate_bill(
                    units,
                    slab_list,
                    fixed_charge,
                    sanctioned_load,
                    surcharge_percent
                )
                forecast_totals.append(total_amount)

            forecast_df["predicted_total"] = forecast_totals
        
        if st.session_state.demo_mode:
            st.info("🚀 Demo Mode Active — Using simulated electricity data.")

        st.markdown("---")
        st.markdown("## Dashboard Summary")

        if not bills_df.empty and future_predictions and len(df_model) >= 6:

            col1, col2, col3 = st.columns(3)

            # -----------------------
            # 📊 Last Month + Growth
            # -----------------------
            last_units = df["units"].iloc[-1]
            prev_units = df["units"].iloc[-2]

            growth = ((last_units - prev_units) / prev_units) * 100

            col1.metric(
                "Last Month Usage (Units)",
                round(last_units, 1),
                delta=f"{round(growth,1)}%"
            )

            # -----------------------
            # 🔮 Forecast + Confidence
            # -----------------------
            forecast_value = future_predictions[0]

            residual_std = df_model["residual"].std()
            forecast_margin = 1.96 * residual_std

            lower_bound = forecast_value - forecast_margin
            upper_bound = forecast_value + forecast_margin

            col2.metric(
                "Next Month Forecast (Units)",
                round(forecast_value, 1)
            )

            st.caption(
                f"Estimated range: {round(lower_bound,1)} – {round(upper_bound,1)} units (95% confidence)"
            )

            # -----------------------
            # 💰 Estimated Bill
            # -----------------------
            if forecast_totals:
                col3.metric(
                    "Estimated Bill (in Rs.)",
                    f"₹ {round(forecast_totals[0], 2)}"
                )
            else:
                col3.metric("Estimated Bill (in Rs.)", "—")
                st.warning("⚙ Please configure slabs & billing settings to see bill forecast.")

            # -----------------------
            # 🔺 Forecast Direction
            # -----------------------
            if forecast_value > last_units:
                st.write("🔺 Forecast indicates increase in consumption next month.")
            else:
                st.write("🔻 Forecast indicates reduction in consumption next month.")

        else:
            st.info("Upload sufficient historical data to activate full dashboard analytics.")

        if not bills_df.empty and future_predictions and len(df_model) >= 6:
            st.markdown("### 🤖 AI Summary")

            summary_text = (
                f"Your usage last month was {round(last_units,1)} units. "
                f"The model forecasts approximately {round(forecast_value,1)} units next month, "
                f"with a {round(abs(growth),1)}% change from the previous month."
            )

            st.info(summary_text)

        st.divider()
        st.subheader("📊 Analytics & Insights")
        
        tab1, tab2, tab3 = st.tabs([
            "📈 Forecast & Planning",
            "🔎 Usage Intelligence",
            "🧪 Model Transparency"
        ])

        with tab1:
            st.subheader("Forecast & Estimated Cost")
            st.dataframe(forecast_df)

            st.subheader("Historical vs Estimated")

            fig, ax = plt.subplots(figsize=(10, 5))

            # Plot historical line
            ax.plot(
                df["date"],
                df["units"],
                label="Actual",
                linewidth=2
            )

            # Plot forecast
            ax.plot(
                forecast_df["date"],
                forecast_df["predicted_units"],
                label="Forecast",
                linestyle="--",
                marker="o"
            )

            # Highlight anomalies
            if not anomalies.empty:
                ax.scatter(
                    anomalies["date"],
                    anomalies["units"],
                    color="red",
                    s=100,
                    label="Anomaly",
                    zorder=5
                )

            # Vertical line at forecast start
            forecast_start = forecast_df["date"].iloc[0]
            ax.axvline(x=forecast_start, linestyle=":", alpha=0.7)

            ax.set_xlabel("Date")
            ax.set_ylabel("Units")
            ax.set_title("Electricity Consumption Forecast")
            ax.legend()

            st.pyplot(fig)


            st.markdown("---")
            st.subheader("What-If Simulation")

            if forecast_totals and future_predictions:
                next_month_units = future_predictions[0]
                next_month_total = forecast_totals[0]

                reduction = st.slider(
                    "Reduce usage by how many units?",
                    min_value=0,
                    max_value=int(next_month_units),
                    value=0
                )

                adjusted_units = next_month_units - reduction

                adjusted_total = calculate_bill(
                    adjusted_units,
                    slab_list,
                    fixed_charge,
                    sanctioned_load,
                    surcharge_percent
                )

                savings = next_month_total - adjusted_total

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Next Month Units",
                    round(next_month_units, 1)
                )

                col2.metric(
                    "Estimated Bill",
                    f"₹ {round(next_month_total, 2)}"
                )

                col3.metric(
                    "If Reduced",
                    f"₹ {round(adjusted_total, 2)}",
                    delta = f"-₹ {round(savings, 2)}" if reduction > 0 else None
                )

                st.write("Adjusted Units:", round(adjusted_units, 2))
                if reduction > 0:
                    st.success(f"💰 You save approximately ₹ {round(savings, 2)}")

                annual_savings = savings * 12
                if reduction > 0:
                    st.write(f"💰 If maintained, this could save approximately ₹ {round(annual_savings, 2)} annually.")


            else:
                next_month_total = 0
                st.warning("⚙ Please configure slabs & billing settings for simulation.")


        with tab2:
            st.subheader("🔎 Usage Intelligence")

            # -----------------------
            # 📈 Trend Analysis
            # -----------------------
            st.markdown("### 📈 Trend Pattern")

            last_6 = df["units"].tail(6)

            if len(last_6) >= 6:
                trend_slope = np.polyfit(range(len(last_6)), last_6, 1)[0]

                if trend_slope > 5:
                    st.info("Consumption is showing a consistent upward trend.")
                elif trend_slope < -5:
                    st.success("Consumption is gradually decreasing.")
                else:
                    st.write("Usage pattern is relatively stable.")

            # -----------------------
            # ☀ Seasonality
            # -----------------------
            st.markdown("### ☀ Seasonal Behavior")

            summer_months = df[df["date"].dt.month.isin([4,5,6,7])]
            winter_months = df[df["date"].dt.month.isin([11,12,1,2])]

            if not summer_months.empty and not winter_months.empty:
                if summer_months["units"].mean() > winter_months["units"].mean():
                    st.write("Higher average consumption observed during summer months.")
                else:
                    st.write("No strong seasonal variation detected.")

            # -----------------------
            # 🚨 Anomaly Explanation
            # -----------------------
            st.markdown("### 🚨 Irregular Usage")

            if not anomalies.empty:
                st.warning("Potential irregular usage detected.")
                for _, row in anomalies.iterrows():
                    st.write(
                        f"{row['date'].strftime('%b %Y')} deviated by "
                        f"{round(row['residual'],1)} units from expected usage."
                    )
            else:
                st.success("No significant anomalies detected.")

            # -----------------------
            # 🏅 Stability Score
            # -----------------------
            st.markdown("### 🏅 Usage Stability Score")

            residual_std = df_model["residual"].std()

            if residual_std < 30:
                score = "A (Very Stable)"
            elif residual_std < 60:
                score = "B (Moderate Variability)"
            else:
                score = "C (High Variability)"

            st.write(f"Your usage stability rating: **{score}**")


        with tab3:
            st.subheader("Model Performance")
            st.dataframe(comparison_df)

            st.subheader("Best Random Forest Parameters")
            st.write(best_params)

            st.subheader("Feature Importance (Random Forest)")
            st.dataframe(importance_df)

            fig2, ax2 = plt.subplots()
            ax2.barh(importance_df["feature"], importance_df["importance"])
            ax2.invert_yaxis()
            ax2.set_title("Feature Importance")
            st.pyplot(fig2)


        with st.expander("Advanced View (Model Inputs)"):
            st.markdown("---")
            st.dataframe(df_model)

    else:
        st.info("No bills uploaded yet.")

st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:15px; font-weight:600;
background: linear-gradient(90deg, #ff7eb3, #65d6ff);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;">
    Made with 🩵 by Ashmi Verma
</div>
""", unsafe_allow_html=True)