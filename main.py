import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import folium
from streamlit_folium import folium_static
from get_news import *
import json

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'power_news' not in st.session_state:
    st.session_state.power_news = False
if 'history' not in st.session_state:
    st.session_state.history = False
if 'email' not in st.session_state:
    st.session_state.email = ''
if 'pwd' not in st.session_state:
    st.session_state.pwd = ''

if not st.session_state.power_news:
    st.session_state.power_news = get_news()
if not st.session_state.history:
    st.session_state.history = get_history()

# Login form
if not st.session_state.logged_in:
    main_screen = st.empty()
    main_screen.write('# ZEUS Power Status Forecast Dashboard')
    with main_screen.form(key='login_form'):
        email = st.text_input('Email Address')
        pwd = st.text_input('Password', type='password')
        submitted = st.form_submit_button('LOGIN')

    if submitted and email == 'admin@zeus.com' and pwd == 'admin':
        st.session_state.logged_in = True
        st.session_state.email = email
        st.session_state.pwd = pwd
        main_screen.empty()  # Clear the login form
else:
    main_screen = st.empty()

# If logged in, display the dashboard
if st.session_state.logged_in:
    # --- Sidebar ---
    st.sidebar.title("Navigation")
    selected_field = st.sidebar.radio(
        "Select Section", ["Overview", "Planned Outages",  "Historical Forecasts"]
    )

    # --- Dashboard Content ---
    st.title("ZEUS Power Status Forecast Dashboard")

    if selected_field == "Overview":
        st.header("Overview")

        # Create beautiful columns for the overview page
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Current Power Status")
            # Example data for current power status
            current_status = pd.DataFrame({
                'Status': ['Operational', 'Maintenance', 'Outage'],
                'Count': [25, 5, 2]
            })
            st.table(current_status)

        with col2:
            st.subheader("Average Power Forecast")
            # Example data for power forecast
            forecast_data = pd.DataFrame({
                'Date': pd.date_range(start='2024-06-01', periods=7, freq='D'),
                'Forecast (MW)': np.random.randint(500, 1000, 7)
            })
            line_chart_forecast = alt.Chart(forecast_data).mark_line().encode(
                x='Date:T',
                y='Forecast (MW):Q'
            )
            st.altair_chart(line_chart_forecast)

    elif selected_field == "Planned Outages":
        st.header("Planned Outages")
        news_data = pd.DataFrame(json.loads(st.session_state.power_news))
        
        # Example data for Power News
        news_data = news_data[['district','work_description','job_condition','date','areas']]
        st.write(news_data)

    elif selected_field == "Power Status":
        st.header("Power Status")
        
        # Example data for Power Status
        status_data = pd.DataFrame({
            'Region': ['North', 'South', 'East', 'West'],
            'Operational': np.random.randint(20, 50, 4),
            'Maintenance': np.random.randint(1, 10, 4),
            'Outage': np.random.randint(0, 5, 4)
        })
        st.write(status_data)

    elif selected_field == "Historical Forecasts":
        st.header("Historical Predictions")
        historical_data = pd.DataFrame(json.loads(st.session_state.history))
        historical_data['status'] = historical_data['status'].astype(int)
        historical_data['confidence'] = historical_data['confidence'].astype(float)
        adj_status = historical_data.apply(calculate_adjusted_status, axis=1)
        v = historical_data.pop('data_id')

        graph_data = historical_data[['area']]
        graph_data['Power Status'] = adj_status
        col1, col2 = st.columns(2)
        st.write(historical_data)
        st.line_chart(graph_data,x='area')
