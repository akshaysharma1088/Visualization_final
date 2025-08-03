
import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.set_page_config(page_title="Childcare Costs Dashboard", layout="centered")
st.title("Childcare Costs in America (2008–2018)")
st.markdown("Explore weekly Family Child Care (FCC) costs by age group using real NDCP data.")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("ndcp_dashboard_data_clean.csv")

df = load_data()

# Sidebar filters
age_groups = df["Age Group"].unique()
selected_age = st.sidebar.selectbox("Select Age Group", age_groups)

min_year = int(df["StudyYear"].min())
max_year = int(df["StudyYear"].max())
selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

# Filtered data
filtered = df[
    (df["Age Group"] == selected_age) &
    (df["StudyYear"] >= selected_years[0]) &
    (df["StudyYear"] <= selected_years[1])
]

# Line chart
fig = px.line(filtered, x="StudyYear", y="Weekly Cost ($)", markers=True,
              title=f"Weekly Cost for {selected_age} Care ({selected_years[0]}–{selected_years[1]})")
fig.update_layout(xaxis_title="Year", yaxis_title="Weekly Cost ($)")
st.plotly_chart(fig)

# Footer
st.markdown("---")
st.markdown("**Source:** National Database of Childcare Prices (NDCP)**  
App by Akshay Sharma")
