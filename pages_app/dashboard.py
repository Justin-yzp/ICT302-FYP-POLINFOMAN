import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np


# Function to create a date range for a given month and year
def get_month_date_range(year, month):
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    return pd.date_range(start_date, end_date)

# Function to create and display the calendar
def create_calendar(year=None, month=None):
    if year is None or month is None:
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

    # Generate the date range for the specified month and year
    date_range = get_month_date_range(year, month)

    # Create a DataFrame to represent the calendar with Sunday as the first day
    calendar_df = pd.DataFrame(index=["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week6"],
                               columns=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])

    # Track previous and next month dates positions
    prev_next_dates = set()

    # Fill the DataFrame with dates from the current month
    start_day = date_range[0].weekday()
    if start_day == 6:
        start_day = 0  # Sunday is day 0
    else:
        start_day += 1  # Shift other days to match Sunday as the first day

    week = 0
    for i, date in enumerate(date_range):
        col = (start_day + i) % 7
        if col == 0 and i != 0:
            week += 1
        calendar_df.iloc[week, col] = date.day

    # Fill in previous month's dates if start_day > 0
    if start_day > 0:
        prev_month = (month - 1) if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_month_end = get_month_date_range(prev_year, prev_month)[-1]
        for i in range(start_day - 1, -1, -1):
            calendar_df.iloc[0, i] = prev_month_end.day
            prev_next_dates.add((0, i))  # Track previous month date position
            prev_month_end -= timedelta(days=1)

        # Fill in next month's dates if the last row has empty slots
    next_month = (month + 1) if month < 12 else 1
    next_year = year if month < 12 else year + 1
    next_month_start = get_month_date_range(next_year, next_month)[0]
    next_date = next_month_start
    for i in range((start_day + len(date_range)) % 7, 7):
        if i == 0 and len(date_range) % 7 != 0:
            week += 1
        calendar_df.iloc[week, i] = next_date.day
        prev_next_dates.add((week, i))  # Track next month date position
        next_date += timedelta(days=1)

    while week < 5:
        week += 1
        for i in range(7):
            calendar_df.iloc[week, i] = next_date.day
            prev_next_dates.add((week, i))  # Track next month date position
            next_date += timedelta(days=1)
        if next_date.month != next_month:
            break

    # Define the styling function to make previous and next month dates translucent
    def highlight_translucent(row):
        return ['color: rgba(0, 0, 0, 0)' if (row.name, idx) in prev_next_dates else 'color: black' for idx in row.index]

    # Apply the styling function
    styled_calendar = calendar_df.style.apply(highlight_translucent, axis=1)


    # Display the calendar without the index
    st.write(f"## {datetime(year, month, 1).strftime('%B %Y')}")
    st.dataframe(styled_calendar, hide_index=True, column_config={"B": None})


def dashboard():
    st.title(f"Welcome, {st.session_state['username']}!")

    st.title("Dashboard")

    st.write("## Calendar")
    # Initialize session state variables
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.now()

    # Date input for selecting a date
    selected_date = st.date_input("Select a date", st.session_state.selected_date)

    # Update session state with the selected date
    if selected_date != st.session_state.selected_date:
        st.session_state.selected_date = selected_date

    selected_year = st.session_state.selected_date.year
    selected_month = st.session_state.selected_date.month

    # Buttons for navigating through months
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous Month"):
            if selected_month == 1:
                selected_month = 12
                selected_year -= 1
            else:
                selected_month -= 1
            st.session_state.selected_date = datetime(selected_year, selected_month, 1)
    with col3:
        if st.button("Next Month"):
            if selected_month == 12:
                selected_month = 1
                selected_year += 1
            else:
                selected_month += 1
            st.session_state.selected_date = datetime(selected_year, selected_month, 1)

    # Call the function to create and display the calendar
    create_calendar(st.session_state.selected_date.year, st.session_state.selected_date.month)