import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
# Set the layout and title for the Streamlit page.
st.set_page_config(
    page_title="Childcare Cost Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed", # Collapse sidebar as it's not used for filters
)

# --- Custom Styling (to match the image) ---
st.markdown("""
<style>
    /* Center the title and subtitle */
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h3 {
        text-align: center;
    }
    /* Style the KPI cards */
    .stMetric {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    /* Center the filters */
    .st-emotion-cache-1r6slb0 {
        display: flex;
        justify-content: center;
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Data Loading and Caching ---
@st.cache_data
def load_data(file_path):
    """
    Loads data from the cleaned CSV file.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please make sure it's in the correct directory.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

    # Rename columns for consistency
    df.rename(columns={
        'StudyYear': 'year',
        'Age Group': 'age_group',
        'Weekly Cost ($)': 'weekly_cost'
    }, inplace=True)
    
    # Ensure age group is capitalized correctly
    df['age_group'] = df['age_group'].str.capitalize()

    return df

# Load the data with the new filename
df_clean = load_data('ndcp_dashboard_data_clean.csv')

# If data loading fails, stop the app
if df_clean is None:
    st.stop()

# --- Main Page Layout ---
st.title("The Rising Cost of Childcare in the U.S.")
st.markdown("<h3 style='font-weight: 400;'>An Interactive Overview (2008-2018)</h3>", unsafe_allow_html=True)


# --- Filters (moved to main body) ---
min_year = int(df_clean['year'].min())
max_year = int(df_clean['year'].max())

# Use columns to place filters side-by-side
filter_col1, filter_col2 = st.columns([1, 3])

with filter_col1:
    # This is a placeholder for the state dropdown from the image.
    # Since the data is national, it's disabled.
    st.text_input("State:", "All (National Data)", disabled=True)

with filter_col2:
    selected_years = st.select_slider(
        "Years:",
        options=range(min_year, max_year + 1),
        value=(min_year, max_year)
    )
start_year, end_year = selected_years


# --- Data Filtering based on selections ---
dff = df_clean[(df_clean['year'] >= start_year) & (df_clean['year'] <= end_year)]


# --- KPI Cards ---
st.markdown("---",) # Visual separator
kpi_data = df_clean[df_clean['year'] == end_year]
kpi_avg_costs = kpi_data.groupby('age_group')['weekly_cost'].mean()

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    infant_cost = kpi_avg_costs.get('Infant', 0)
    st.metric(
        label="Avg. Infant Cost",
        value=f"${infant_cost:.1f}",
        help=f"National average for {end_year}"
    )
with kpi_col2:
    toddler_cost = kpi_avg_costs.get('Toddler', 0)
    st.metric(
        label="Avg. Toddler Cost",
        value=f"${toddler_cost:.1f}",
        help=f"National average for {end_year}"
    )
with kpi_col3:
    preschool_cost = kpi_avg_costs.get('Preschool', 0)
    st.metric(
        label="Avg. Preschool Cost",
        value=f"${preschool_cost:.1f}",
        help=f"National average for {end_year}"
    )
st.markdown("---",) # Visual separator


# --- Line Chart ---
st.markdown("<h3 style='font-weight: 400;'>Weekly Cost Trends</h3>", unsafe_allow_html=True)
line_data = dff.groupby(['year', 'age_group'])['weekly_cost'].mean().reset_index()
line_fig = px.line(
    line_data,
    x='year',
    y='weekly_cost',
    color='age_group',
    labels={'weekly_cost': 'Avg. Weekly Cost ($)', 'year': 'Year', 'age_group': 'Age Group'},
    color_discrete_map={
        'Infant': '#636EFA', # A blue color
        'Toddler': '#AB63FA', # A purple color
        'Preschool': '#00CC96'  # A green color
    }
)
line_fig.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='rgba(240, 242, 246, 0.75)' # Light gray background for the plot area
)
st.plotly_chart(line_fig, use_container_width=True)
