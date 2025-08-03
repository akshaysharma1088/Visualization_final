import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Childcare Cost Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom Styling ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h3 {
        text-align: center;
    }
    .stMetric {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)


# --- Data Loading and Caching ---
@st.cache_data
def load_data(file_path):
    """
    Loads data from the original CSV file, cleans, and reshapes it.
    """
    try:
        # Using read_csv and handling potential encoding issues.
        df = pd.read_csv(file_path, encoding='latin1')
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

# Load the data with the original filename
df_clean = load_data('nationaldatabaseofchildcareprices.xlsx - nationaldatabaseofchildcare.csv')

# If data loading fails, stop the app
if df_clean is None:
    st.stop()

# --- Main Page Layout ---
st.title("The Rising Cost of Childcare in the U.S.")
st.markdown("<h3 style='font-weight: 400;'>An Interactive Overview (2008-2018)</h3>", unsafe_allow_html=True)


# --- Filters ---
min_year = int(df_clean['year'].min())
max_year = int(df_clean['year'].max())
state_options = ['All States'] + sorted(df_clean['state_name'].unique())

filter_col1, filter_col2 = st.columns([1, 3])

with filter_col1:
    selected_state = st.selectbox("State:", options=state_options, index=0)

with filter_col2:
    selected_years = st.select_slider(
        "Years:",
        options=range(min_year, max_year + 1),
        value=(min_year, max_year)
    )
start_year, end_year = selected_years


# --- Data Filtering based on selections ---
if selected_state == 'All States':
    dff = df_clean[(df_clean['year'] >= start_year) & (df_clean['year'] <= end_year)]
else:
    dff = df_clean[(df_clean['state_name'] == selected_state) &
                   (df_clean['year'] >= start_year) &
                   (df_clean['year'] <= end_year)]


# --- KPI Cards ---
st.markdown("---")
kpi_data = df_clean[df_clean['year'] == end_year]
if selected_state != 'All States':
    kpi_data = kpi_data[kpi_data['state_name'] == selected_state]

kpi_avg_costs = kpi_data.groupby('age_group')['weekly_cost'].mean()

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    infant_cost = kpi_avg_costs.get('Infant', 0)
    st.metric(label="Avg. Infant Cost", value=f"${infant_cost:.1f}", help=f"Average for {selected_state} in {end_year}")
with kpi_col2:
    toddler_cost = kpi_avg_costs.get('Toddler', 0)
    st.metric(label="Avg. Toddler Cost", value=f"${toddler_cost:.1f}", help=f"Average for {selected_state} in {end_year}")
with kpi_col3:
    preschool_cost = kpi_avg_costs.get('Preschool', 0)
    st.metric(label="Avg. Preschool Cost", value=f"${preschool_cost:.1f}", help=f"Average for {selected_state} in {end_year}")
st.markdown("---")


# --- Visualizations ---
viz_col1, viz_col2 = st.columns([3, 2]) # 3 parts for line chart, 2 for map

with viz_col1:
    st.markdown("<h3 style='font-weight: 400;'>Weekly Cost Trends</h3>", unsafe_allow_html=True)
    line_data = dff.groupby(['year', 'age_group'])['weekly_cost'].mean().reset_index()
    line_fig = px.line(
        line_data,
        x='year',
        y='weekly_cost',
        color='age_group',
        labels={'weekly_cost': 'Avg. Weekly Cost ($)', 'year': 'Year', 'age_group': 'Age Group'},
        color_discrete_map={'Infant': '#636EFA', 'Toddler': '#AB63FA', 'Preschool': '#00CC96'}
    )
    line_fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(240, 242, 246, 0.75)'
    )
    st.plotly_chart(line_fig, use_container_width=True)

with viz_col2:
    st.markdown(f"<h3 style='font-weight: 400;'>Avg. Weekly Infant Cost in {end_year}</h3>", unsafe_allow_html=True)
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
    map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, geo=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(map_fig, use_container_width=True)
