import streamlit as st
from streamlit_calendar import calendar
import sqlite3
from datetime import datetime, timedelta

# Connect to the SQLite database
db_path = r'C:\Users\zhanp\OneDrive\Desktop\ICT302-main\utils\governance_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Utility functions to fetch data
def fetch_all_dates():
    cursor.execute('SELECT file_name, date_effective, review_date FROM Governance')
    return cursor.fetchall()

def fetch_upcoming_events():
    cursor.execute('''
    SELECT file_name, date_effective, review_date
    FROM Governance
    WHERE (strftime('%Y-%m-%d', date_effective) >= strftime('%Y-%m-%d', 'now')) 
       OR (strftime('%Y-%m-%d', review_date) >= strftime('%Y-%m-%d', 'now'))
    ''')
    return cursor.fetchall()

# Fetch data
all_dates = fetch_all_dates()
upcoming_events = fetch_upcoming_events()

# Prepare data for calendar
calendar_events = []
for record in all_dates:
    if record[1]:  # date_effective
        calendar_events.append({
            'title': f"Effective Date of {record[0]}",
            'start': record[1].split()[0],  # Strip time part
            'color': 'blue',
            'extendedProps': {
                'description': f'This is the effective date of {record[0]}'
            }
        })
    if record[2]:  # review_date
        calendar_events.append({
            'title': f"Review Date of {record[0]}",
            'start': record[2].split()[0],  # Strip time part
            'color': 'red',
            'extendedProps': {
                'description': f'This is the review date of {record[0]}'
            }
        })

# Streamlit UI
st.title('Governance Calendar')

# Create columns for the calendar and upcoming events
col1, col2 = st.columns([2, 1])  # Calendar takes up 2/3 of the space

# Calendar visualization
with col1:
    st.write("### Calendar with Important Dates")
    # Create and display the calendar
    calendar_component = calendar(events=calendar_events, options={
        'headerToolbar': {
            'left': 'prev,next today',
            'center': 'title',
            'right': 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        'initialView': 'dayGridMonth',
        'navLinks': True,  # can click day/week names to navigate views
        'editable': True,
        'dayMaxEvents': True,  # allow "more" link when too many events
        'eventColor': '#378006'
    })
    st.write(calendar_component)

# Display upcoming events in the second column
with col2:
    st.title('Upcoming Events')
    for event in upcoming_events:
        if event[1]:  # date_effective
            st.markdown(f"**Effective Date of {event[0]}**: {event[1]}")
        if event[2]:  # review_date
            st.markdown(f"**Review Date of {event[0]}**: {event[2]}")

# Close the database connection
conn.close()
