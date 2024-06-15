import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from get_data import *
import json


# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'power_news' not in st.session_state:
    st.session_state.power_news = False
if 'history' not in st.session_state:
    st.session_state.history = False
if 'reports' not in st.session_state:
    st.session_state.reports = False
if 'users' not in st.session_state:
    st.session_state.users = False
if 'email' not in st.session_state:
    st.session_state.email = ''
if 'pwd' not in st.session_state:
    st.session_state.pwd = ''

if not st.session_state.power_news:
    st.session_state.power_news = get_news()
if not st.session_state.history:
    st.session_state.history = get_history()
if not st.session_state.reports:
    st.session_state.reports = get_reports()
if not st.session_state.users:
    st.session_state.users = get_users()

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
        "Select Section", ["Overview", "Planned Outages", "Outage Reports", "Historical Forecasts", "User Management"]
    )

    # --- Dashboard Content ---
    st.title("ZEUS Power Status Forecast Dashboard")

    if selected_field == "Overview":
        st.header("Overview")

        # Create beautiful columns for the overview page
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Summary of Various Sections")

            # Get data from session state
            planned_outages_data = pd.DataFrame(json.loads(st.session_state.power_news))
            outage_reports_data = pd.DataFrame(json.loads(st.session_state.reports))
            historical_forecasts_data = pd.DataFrame(json.loads(st.session_state.history))
            users_data = pd.DataFrame(json.loads(st.session_state.users))

            # Create summary data
            summary_data = {
                'Section': ['Planned Outages', 'Outage Reports', 'Historical Forecasts', 'Users'],
                'Count': [
                    planned_outages_data.shape[0],
                    outage_reports_data.shape[0],
                    historical_forecasts_data.shape[0],
                    users_data.shape[0]
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            st.table(summary_df)

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
        news_data = news_data[['district', 'work_description', 'job_condition', 'date', 'areas']]
        st.write(news_data)

    elif selected_field == "Outage Reports":
        st.header("Outage Reports")

        # Fetch outage reports from session state
        reports_data = pd.DataFrame(json.loads(st.session_state.reports))

        # Extract location_name from location
        reports_data['location_name'] = reports_data['location'].apply(lambda x: json.loads(x)['locationName'])

        # Display relevant columns, including location_name
        st.dataframe(reports_data[['user_id', 'location_name', 'description', 'reported_when']])

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
        st.line_chart(graph_data, x='area')

    elif selected_field == "User Management":
        st.header("User Management")
        
        # Fetch user data from session state
        users_data = pd.DataFrame(json.loads(st.session_state.users))
        
        # Display all columns in the dataframe
        st.dataframe(users_data)

        # Section for sending notifications
        st.subheader("Send Notifications")

        # Custom news input
        custom_news = st.text_area("Custom News")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("SEND POWER NEWS"):
                if send_news():
                    st.success("Power News sent to all users!")

        with col2:
            if st.button("SEND CUSTOM NEWS"):
                if custom_news:
                    if send_news(custom_news):
                        st.success("Custom News sent to all users!")
                else:
                    st.warning("Please enter custom news to send.")
