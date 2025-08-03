
import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.title("Childcare Costs in America (2008–2018)")
st.markdown("An interactive dashboard based on the National Database of Childcare Prices (NDCP).")

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv"  # placeholder
    return pd.read_csv(url)

# Simulated placeholder data (replace with real dataset in actual deployment)
data = pd.DataFrame({
    "Year": list(range(2008, 2019)) * 3,
    "Age Group": ["Infant"] * 11 + ["Toddler"] * 11 + ["Preschool"] * 11,
    "Weekly Cost": [97 + i*1.5 for i in range(11)] + [90 + i*1.4 for i in range(11)] + [88 + i*1.2 for i in range(11)]
})

# Sidebar filter
age_group = st.sidebar.selectbox("Select Age Group", data["Age Group"].unique())
filtered = data[data["Age Group"] == age_group]

# Line chart
fig = px.line(filtered, x="Year", y="Weekly Cost", title=f"Weekly {age_group} Care Cost (75th Percentile)")
st.plotly_chart(fig)

# Footer
st.markdown("---")
st.markdown("**Source:** National Database of Childcare Prices (NDCP)  
App by Akshay Sharma")
