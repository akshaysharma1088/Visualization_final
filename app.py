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
    # FIX: Include 'studyyear' in the base columns as it contains the year information.
    base_cols = ['state_name', 'state_abbreviation', 'county_name', 'studyyear']
    
    # Identify cost columns based on a flexible pattern
    cost_cols = [
        col for col in df.columns 
        if 'fcc' in col and any(age in col for age in ['infant', 'toddler', 'preschool'])
    ]
    
    if not all(col in df.columns for col in base_cols) or not cost_cols:
        st.error("The data file is missing required columns (e.g., 'state_name', 'studyyear', or cost data).")
        return None

    df_filtered = df[base_cols + cost_cols]
    df_melted = df_filtered.melt(id_vars=base_cols, var_name='metric', value_name='weekly_cost')
    
    # Safely extract age group from the 'metric' column
    df_melted['age_group_str'] = df_melted['metric'].str.extract(r'(infant|toddler|preschool)')[0]

    # Drop rows where extraction failed or cost is missing
    df_melted.dropna(subset=['studyyear', 'age_group_str', 'weekly_cost'], inplace=True)

    # Safely convert data types
    if not df_melted.empty:
        # FIX: Use the 'studyyear' column for the year.
        df_melted['year'] = df_melted['studyyear'].astype(int)
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

col1, col2, col3 = st.columns(3)
with col1:
    infant_cost = kpi_avg_costs.get('Infant', 0)
    st.metric(
        label=f"Avg. Infant Weekly Cost ({end_year})",
        value=f"${infant_cost:.0f}",
        help=f"Based on 75th percentile Family Child Care costs in {selected_state}."
    )
with col2:
    toddler_cost = kpi_avg_costs.get('Toddler', 0)
    st.metric(
        label=f"Avg. Toddler Weekly Cost ({end_year})",
        value=f"${toddler_cost:.0f}"
    )
with col3:
    preschool_cost = kpi_avg_costs.get('Preschool', 0)
    st.metric(
        label=f"Avg. Preschool Weekly Cost ({end_year})",
        value=f"${preschool_cost:.0f}"
    )


# --- Visualizations ---
st.markdown("---")
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader(f"Weekly Cost Trends in {selected_state}")
    line_data = dff.groupby(['year', 'age_group'])['weekly_cost'].mean().reset_index()
    line_fig = go.Figure()
    for age, color in [('Infant', '#22d3ee'), ('Toddler', '#c084fc'), ('Preschool', '#4ade80')]:
        trace_data = line_data[line_data['age_group'] == age]
        line_fig.add_trace(go.Scatter(x=trace_data['year'], y=trace_data['weekly_cost'], name=age, mode='lines+markers', line_color=color))
    line_fig.update_layout(yaxis_title='Avg. Weekly Cost ($)')
    st.plotly_chart(line_fig, use_container_width=True)

with col_right:
    st.subheader(f"Avg. Weekly Infant Cost in {end_year}")
    map_data = df_clean[(df_clean['year'] == end_year) & (df_clean['age_group'] == 'Infant')]
    map_avg_data = map_data.groupby('state_abbreviation')['weekly_cost'].mean().reset_index()
    map_fig = go.Figure(data=go.Choropleth(
        locations=map_avg_data['state_abbreviation'],
        locationmode="USA-states",
        z=map_avg_data['weekly_cost'],
        colorscale='Teal',
        colorbar_title='Avg. Weekly Cost'
    ))
    map_fig.update_layout(geo_scope='usa')
    st.plotly_chart(map_fig, use_container_width=True)
