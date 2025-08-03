import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
# Set the layout and title for the Streamlit page. This should be the first Streamlit command.
st.set_page_config(
    page_title="Childcare Cost Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Data Loading and Caching ---
# Use st.cache_data to load and process the data only once, improving performance.
@st.cache_data
def load_data(file_path):
    """
    Loads data from a CSV file, cleans it, and reshapes it for analysis.
    """
    try:
        # Switched to read_csv for the new file format
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please make sure it's in the correct directory.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

    # Reshape and clean the data
    base_cols = ['state_name', 'state_abbreviation', 'county_name']
    cost_cols = [col for col in df.columns if '_75fcc' in col.lower()]
    df_filtered = df[base_cols + cost_cols]
    df_melted = df_filtered.melt(id_vars=base_cols, var_name='metric', value_name='weekly_cost')
    df_melted['year'] = df_melted['metric'].str.extract(r'(\d{4})').astype(int)
    df_melted['age_group'] = df_melted['metric'].str.extract(r'fcc(infant|toddler|preschool)')[0].str.capitalize()
    df_clean = df_melted.dropna(subset=['weekly_cost', 'age_group', 'year'])
    return df_clean

# Load the data with the new filename
df_clean = load_data('ndcp_dashboard_data_clean.csv')

# If data loading fails, stop the app
if df_clean is None:
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters")

# State selection dropdown
state_options = ['All States'] + sorted(df_clean['state_name'].unique())
selected_state = st.sidebar.selectbox(
    "Select a State",
    options=state_options,
    index=0 # Default to 'All States'
)

# Year range slider
min_year = int(df_clean['year'].min())
max_year = int(df_clean['year'].max())
selected_years = st.sidebar.select_slider(
    "Select a Year Range",
    options=range(min_year, max_year + 1),
    value=(min_year, max_year)
)
start_year, end_year = selected_years

# --- Main Page Layout ---
st.title("💸 The Rising Cost of Childcare in the U.S.")
st.markdown(f"An Interactive Overview from **{start_year}** to **{end_year}**")

# --- Data Filtering based on selections ---
if selected_state == 'All States':
    dff = df_clean[(df_clean['year'] >= start_year) & (df_clean['year'] <= end_year)]
else:
    dff = df_clean[(df_clean['state_name'] == selected_state) &
                   (df_clean['year'] >= start_year) &
                   (df_clean['year'] <= end_year)]

# --- KPI Cards ---
st.markdown("### Key Metrics")
kpi_data = df_clean[df_clean['year'] == end_year]
if selected_state != 'All States':
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
col_left, col_right = st.columns([3, 2]) # Make the left column wider

with col_left:
    # --- Line Chart ---
    st.subheader("Weekly Childcare Cost Trends")
    line_data = dff.groupby(['year', 'age_group'])['weekly_cost'].mean().reset_index()
    line_fig = px.line(
        line_data,
        x='year',
        y='weekly_cost',
        color='age_group',
        title=f"Cost Trends in {selected_state}",
        labels={'weekly_cost': 'Avg. Weekly Cost ($)', 'year': 'Year'},
        color_discrete_map={
            'Infant': '#22d3ee',
            'Toddler': '#c084fc',
            'Preschool': '#4ade80'
        }
    )
    line_fig.update_layout(
        legend_title_text='',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(line_fig, use_container_width=True)

with col_right:
    # --- Map ---
    st.subheader(f"Avg. Infant Cost by State ({end_year})")
    map_data = df_clean[(df_clean['year'] == end_year) & (df_clean['age_group'] == 'Infant')]
    map_avg_data = map_data.groupby('state_abbreviation')['weekly_cost'].mean().reset_index()

    map_fig = px.choropleth(
        map_avg_data,
        locations='state_abbreviation',
        locationmode="USA-states",
        color='weekly_cost',
        scope="usa",
        color_continuous_scale=px.colors.sequential.Teal,
        labels={'weekly_cost': 'Avg. Weekly Cost'}
    )
    map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(map_fig, use_container_width=True)

