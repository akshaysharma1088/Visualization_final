import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Childcare Cost Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Data Loading and Caching ---
@st.cache_data
def load_data(file_path):
    """
    Loads data from the sampled CSV file, cleans, and reshapes it.
    """
    try:
        df = pd.read_csv(file_path, encoding='latin1')
        # Convert all column names to lowercase to prevent KeyErrors
        df.columns = df.columns.str.lower()
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please make sure it's in the correct directory.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

    # Reshape and clean the data
    base_cols = ['state_name', 'state_abbreviation', 'county_name']
    # Identify cost columns based on a flexible pattern
    cost_cols = [
        col for col in df.columns 
        if 'fcc' in col and any(age in col for age in ['infant', 'toddler', 'preschool'])
    ]
    
    if not all(col in df.columns for col in base_cols) or not cost_cols:
        st.error("The data file is missing required columns (e.g., 'state_name' or cost data).")
        return None

    df_filtered = df[base_cols + cost_cols]
    df_melted = df_filtered.melt(id_vars=base_cols, var_name='metric', value_name='weekly_cost')
    
    # Safely extract year and age group from the 'metric' column
    df_melted['year_str'] = df_melted['metric'].str.extract(r'(\d{4})')
    df_melted['age_group_str'] = df_melted['metric'].str.extract(r'(infant|toddler|preschool)')[0]

    # Drop rows where extraction failed
    df_melted.dropna(subset=['year_str', 'age_group_str', 'weekly_cost'], inplace=True)

    # Safely convert data types
    if not df_melted.empty:
        df_melted['year'] = df_melted['year_str'].astype(int)
        df_melted['age_group'] = df_melted['age_group_str'].str.capitalize()
    
    return df_melted

# Load the data from the sampled CSV
df_clean = load_data('nationaldatabaseofchildcare_sampled.csv')

# If data loading fails, stop the app
if df_clean is None or df_clean.empty:
    st.error("Data could not be loaded or is empty after cleaning. Please check the file and column names.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters")

# State selection dropdown
state_options = ['All'] + sorted(df_clean['state_name'].unique())
selected_state = st.sidebar.selectbox(
    "Select a State",
    options=state_options,
    index=0 
)

# Year range slider
min_year = int(df_clean['year'].min())
max_year = int(df_clean['year'].max())
selected_years = st.sidebar.slider(
    "Select a Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)
start_year, end_year = selected_years

# --- Main Page Layout ---
st.title("The Rising Cost of Childcare in the U.S.")
st.markdown(f"An Interactive Overview from **{start_year}** to **{end_year}**")

# --- Data Filtering based on selections ---
if selected_state == 'All':
    dff = df_clean[(df_clean['year'] >= start_year) & (df_clean['year'] <= end_year)]
else:
    dff = df_clean[(df_clean['state_name'] == selected_state) &
                   (df_clean['year'] >= start_year) &
                   (df_clean['year'] <= end_year)]

# --- KPI Cards ---
st.markdown("### Key Metrics")
kpi_data = df_clean[df_clean['year'] == end_year]
if selected_state != 'All':
    kpi_data = kpi_data[kpi_data['state_name'] == selected_state]

kpi_avg_costs = kpi_data.groupby('age_group')['weekly_cost'].mean()

col1, c
