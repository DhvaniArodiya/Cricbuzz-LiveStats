import streamlit as st
import pandas as pd
import joblib
import numpy as np
from datetime import datetime
import plotly.express as px

# PAGE CONFIG 
st.set_page_config(
    page_title="Real Estate Investment Advisor",
    layout="wide",
    page_icon="🏠"
)

# GLOBAL STYLE (CSS)
st.markdown(
    """
    <style>
        /* Main background */
        .stApp {
            background: radial-gradient(circle at top left, #0ea5e9 0, #020617 45%, #020617 100%);
            color: #e5e7eb;
        }
        /* Card-like containers */
        .card {
            padding: 1.2rem 1.5rem;
            border-radius: 1rem;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.4);
            box-shadow: 0 18px 35px rgba(15, 23, 42, 0.9);
            margin-bottom: 1rem;
        }
        /* Metrics styling */
        div[data-testid="metric-container"] {
            background-color: rgba(15, 23, 42, 0.95);
            border-radius: 0.75rem;
            padding: 0.75rem 0.75rem;
            border: 1px solid rgba(148, 163, 184, 0.45);
        }
        div[data-testid="metric-container"] > label {
            color: #9ca3af;
        }
        div[data-testid="metric-container"] > div {
            color: #e5e7eb;
        }
        /* Titles */
        h1, h2, h3, h4 {
            color: #f9fafb !important;
        }
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #020617;
        }
        /* Buttons */
        .stButton>button {
            border-radius: 999px;
            padding: 0.6rem 1.3rem;
            background: linear-gradient(to right, #22c55e, #0ea5e9);
            color: white;
            border: none;
        }
        .stButton>button:hover {
            filter: brightness(1.08);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Load Models & Data
@st.cache_resource
def load_models():
    cls = joblib.load("models/good_investment_classifier.joblib")
    reg = joblib.load("models/future_price_regressor.joblib")
    return cls, reg

@st.cache_data
def load_data():
    return pd.read_csv("india_housing_prices.csv")

cls_pipeline, reg_pipeline = load_models()
data = load_data()

# HEADER
st.markdown(
    """
    <div class="card" style="margin-bottom: 1.5rem;">
        <h1>🏠 Real Estate Investment Advisor</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# SIDEBAR FILTERS
st.sidebar.title("🔍 Filters")

min_price, max_price = float(data["Price_in_Lakhs"].min()), float(data["Price_in_Lakhs"].max())
price_range = st.sidebar.slider(
    "Price Range (Lakhs)",
    min_price, max_price,
    (min_price, max_price)
)

bhk_filter = st.sidebar.multiselect(
    "BHK",
    options=sorted(data["BHK"].unique()),
    default=sorted(data["BHK"].unique())
)

city_filter = st.sidebar.multiselect(
    "City",
    options=sorted(data["City"].unique()),
    default=list(data["City"].unique())[:5]
)

filtered = data[
    (data["Price_in_Lakhs"].between(price_range[0], price_range[1])) &
    (data["BHK"].isin(bhk_filter)) &
    (data["City"].isin(city_filter))
]

st.sidebar.markdown("---")
st.sidebar.metric("Filtered Properties", len(filtered))


# LAYOUT: TABS
tab1, tab2 = st.tabs(["🔮 Investment Prediction & Report", "📊 Market Analytics"])

# TAB 1: PREDICTION + REPORT
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Property Input")

    col1, col2, col3 = st.columns(3)

    with col1:
        state = st.selectbox("State", sorted(data["State"].unique()))
        city = st.selectbox("City", sorted(data[data["State"] == state]["City"].unique()))
        locality = st.selectbox("Locality", sorted(data[data["City"] == city]["Locality"].unique()))
        property_type = st.selectbox("Property Type", sorted(data["Property_Type"].unique()))

    with col2:
        bhk = st.number_input("BHK", 1, 10, 3)
        size_sqft = st.number_input("Size (SqFt)", 200, 15000, 1200)
        price_lakhs = st.number_input("Current Price (Lakhs)", 5.0, 5000.0, 100.0)
        year_built = st.number_input("Year Built", 1950, 2025, 2015)

    with col3:
        furnished_status = st.selectbox("Furnished Status", data["Furnished_Status"].unique())
        availability_status = st.selectbox("Availability Status", data["Availability_Status"].unique())
        parking_space = st.selectbox("Parking Space", data["Parking_Space"].unique())
        public_transport = st.selectbox(
            "Public Transport Accessibility",
            data["Public_Transport_Accessibility"].unique()
        )
        facing = st.selectbox("Facing", data["Facing"].unique())

    col4, col5, col6 = st.columns(3)
    with col4:
        nearby_schools = st.slider("Nearby Schools (0–10)", 0, 10, 3)
    with col5:
        nearby_hospitals = st.slider("Nearby Hospitals (0–10)", 0, 10, 3)
    with col6:
        floor_no = st.number_input("Floor No", 0, 100, 1)

    col7, col8 = st.columns(2)
    with col7:
        total_floors = st.number_input("Total Floors", 1, 100, 5)
    with col8:
        amenity_count = st.slider("Amenity Count", 0, 20, 5)

    # --------------- Derived Features ----------------
    age_of_property = 2025 - year_built
    price_per_sqft = price_lakhs * 100000 / max(size_sqft, 1)

    school_density = nearby_schools / 10
    hospital_density = nearby_hospitals / 10

    is_furnished = int(furnished_status in ["Furnished", "Semi-furnished"])
    is_ready = int("Ready" in str(availability_status))
    has_parking = int(str(parking_space).lower() in ["yes", "covered", "open"])
    has_security = 1

    facing_map = {"North": 0, "East": 1, "West": 2, "South": 3}
    facing_code = facing_map.get(facing, 0)

    st.markdown('</div>', unsafe_allow_html=True) 

    # --------------- Prediction & Report ---------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button("🔍 Run Investment Analysis", use_container_width=True):

        input_row = {
            "State": state,
            "City": city,
            "Locality": locality,
            "Property_Type": property_type,
            "BHK": bhk,
            "Size_in_SqFt": size_sqft,
            "Price_in_Lakhs": price_lakhs,
            "Price_per_SqFt": price_per_sqft,
            "Year_Built": year_built,
            "Furnished_Status": furnished_status,
            "Floor_No": floor_no,
            "Total_Floors": total_floors,
            "Age_of_Property": age_of_property,
            "Nearby_Schools": nearby_schools,
            "Nearby_Hospitals": nearby_hospitals,
            "Public_Transport_Accessibility": public_transport,
            "Parking_Space": parking_space,
            "Security": "Yes",
            "Facing": facing,
            "Owner_Type": "Owner",
            "Availability_Status": availability_status,
            "Amenity_Count": amenity_count,
            "Is_Furnished": is_furnished,
            "Is_Ready_To_Move": is_ready,
            "Has_Parking": has_parking,
            "Has_Security": has_security,
            "School_Density_Score": school_density,
            "Hospital_Density_Score": hospital_density,
            "Facing_Code": facing_code
        }

        input_df = pd.DataFrame([input_row])

        invest_pred = cls_pipeline.predict(input_df)[0]
        future_price = reg_pipeline.predict(input_df)[0]

        # Pretty display
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            if invest_pred == 1:
                st.success("✅ This property is classified as a **GOOD INVESTMENT**.")
                invest_text = "GOOD INVESTMENT"
            else:
                st.error("⚠️ This property is classified as **NOT A GOOD INVESTMENT**.")
                invest_text = "NOT A GOOD INVESTMENT"

        with col_res2:
            st.metric("Estimated Price After 5 Years (Lakhs)", f"{future_price:.2f}")

        # ---------- BUILD HTML REPORT ----------
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        details_html = input_df.T
        details_html.columns = ["Value"]
        details_html = details_html.to_html(
            border=1,
            classes="details-table",
            justify="left"
        )

        report_html = f"""
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Real Estate Investment Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    background-color: #0b1220;
                    color: #e5e7eb;
                }}
                h1 {{ color: #f9fafb; }}
                h2 {{ margin-top: 24px; color: #e5e7eb; }}
                .summary-box {{
                    padding: 12px 16px;
                    border-radius: 10px;
                    background: linear-gradient(90deg, #22c55e33, #0ea5e933);
                    border: 1px solid #22c55e66;
                    margin-bottom: 16px;
                }}
                .good {{ color: #22c55e; font-weight: bold; }}
                .bad {{ color: #ef4444; font-weight: bold; }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 10px;
                }}
                th, td {{
                    border: 1px solid #374151;
                    padding: 6px 8px;
                    text-align: left;
                    font-size: 13px;
                }}
                th {{
                    background-color: #111827;
                }}
                .footer {{
                    margin-top: 32px;
                    font-size: 12px;
                    color: #9ca3af;
                }}
            </style>
        </head>
        <body>
            <h1>Real Estate Investment Report</h1>
            <div class="summary-box">
                <p><strong>Generated on:</strong> {report_time}</p>
                <p><strong>Prediction Result:</strong>
                    <span class="{{ 'good' if {invest_pred} == 1 else 'bad' }}">
                        {invest_text}
                    </span>
                </p>
                <p><strong>Estimated Price After 5 Years:</strong>
                    ₹{future_price:.2f} Lakhs
                </p>
            </div>

            <h2>Property Details</h2>
            {details_html}

            <div class="footer">
                <p>Real Estate Investment Advisor – ML-powered decision support system.</p>
            </div>
        </body>
        </html>
        """

        st.markdown("### 📥 Download Full Investment Report")
        st.download_button(
            label="⬇ Download Full Investment Report",
            data=report_html.encode("utf-8"),
            file_name="investment_report.html",
            mime="text/html"
        )

    st.markdown('</div>', unsafe_allow_html=True)  

# TAB 2: MARKET ANALYTICS (FILTERED DATA)
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧮 Property Metrics (Filtered Data)")

    if not filtered.empty:
        total_props = len(filtered)
        avg_price = filtered["Price_in_Lakhs"].mean()
        median_price = filtered["Price_in_Lakhs"].median()
        avg_pps = filtered["Price_per_SqFt"].mean()
        avg_bhk = filtered["BHK"].mean()
        pct_good = 100 * filtered["Good_Investment"].mean()

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Properties", f"{total_props}")
        with m2:
            st.metric("Avg Price (Lakhs)", f"{avg_price:.2f}")
        with m3:
            st.metric("Median Price (Lakhs)", f"{median_price:.2f}")

        m4, m5, m6 = st.columns(3)
        with m4:
            st.metric("Avg Price per SqFt", f"{avg_pps:.2f}")
        with m5:
            st.metric("Avg BHK", f"{avg_bhk:.2f}")
        with m6:
            st.metric("% Good Investments", f"{pct_good:.1f}%")
    else:
        st.info("No properties match the current filters to compute metrics.")

    st.markdown('</div>', unsafe_allow_html=True)

    # --------- Charts ----------
    if not filtered.empty:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Interactive Charts (Filtered Data)")

        colA, colB = st.columns(2)

        with colA:
            state_pps = (
                filtered.groupby("State")["Price_per_SqFt"]
                .mean()
                .reset_index()
                .sort_values("Price_per_SqFt", ascending=False)
            )
            fig1 = px.bar(
                state_pps,
                x="State",
                y="Price_per_SqFt",
                title="Average Price per SqFt by State",
            )
            fig1.update_layout(height=400, xaxis_tickangle=-45, template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)

        with colB:
            city_invest = (
                filtered.groupby(["City", "Good_Investment"])
                .size()
                .reset_index(name="Count")
            )
            city_invest["Investment"] = city_invest["Good_Investment"].map(
                {1: "Good", 0: "Not Good"}
            )
            fig2 = px.bar(
                city_invest,
                x="City",
                y="Count",
                color="Investment",
                barmode="group",
                title="Good vs Not Good Investments by City",
            )
            fig2.update_layout(height=400, xaxis_tickangle=-45, template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        # Scatter: Price vs BHK
        fig3 = px.scatter(
            filtered,
            x="BHK",
            y="Price_in_Lakhs",
            color="City",
            hover_data=["Locality", "Price_per_SqFt"],
            title="Price vs BHK (Filtered Data)",
        )
        fig3.update_layout(height=430, template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Adjust filters in the sidebar to see analytics charts.")