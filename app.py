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

# --- Sidebar Filters ---
st.sidebar.header("Dashboard Filters")

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
st.markdown(f"An Interactive Overview of National Averages from **{start_year}** to **{end_year}**")

# --- Data Filtering based on selections ---
dff = df_clean[(df_clean['year'] >= start_year) & (df_clean['year'] <= end_year)]

# --- KPI Cards ---
st.markdown("### Key Metrics")
kpi_data = df_clean[df_clean['year'] == end_year]

kpi_avg_costs = kpi_data.groupby('age_group')['weekly_cost'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    infant_cost = kpi_avg_costs.get('Infant', 0)
    st.metric(
        label=f"Avg. Infant Weekly Cost ({end_year})",
        value=f"${infant_cost:.0f}",
        help="Based on national 75th percentile Family Child Care costs."
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

# --- Line Chart ---
st.subheader("National Weekly Childcare Cost Trends")
line_data = dff.groupby(['year', 'age_group'])['weekly_cost'].mean().reset_index()
line_fig = px.line(
    line_data,
    x='year',
    y='weekly_cost',
    color='age_group',
    title="Average National Cost Trends by Age Group",
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
