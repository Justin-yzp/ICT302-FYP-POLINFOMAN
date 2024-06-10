import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import calendar
import plotly.express as px

# Connect to the SQLite database
db_path = r'C:\Users\zhanp\OneDrive\Desktop\ICT302-main\utils\governance_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Utility functions to fetch data
def fetch_all_dates():
    cursor.execute('SELECT file_name, date_effective, review_date FROM Governance')
    return cursor.fetchall()

def fetch_upcoming_events():
    one_year_later = datetime.now() + timedelta(days=365)
    cursor.execute('''
    SELECT file_name, date_effective, review_date
    FROM Governance
    WHERE (date_effective BETWEEN DATE('now') AND ?) 
       OR (review_date BETWEEN DATE('now') AND ?)
    ''', (one_year_later, one_year_later))
    return cursor.fetchall()

# Fetch data
all_dates = fetch_all_dates()
upcoming_events = fetch_upcoming_events()

# Prepare data for calendar
calendar_data = []
for record in all_dates:
    if record[1]:  # date_effective
        calendar_data.append({
            'date': record[1].split()[0],  # Strip time part
            'event': f"Effective Date of {record[0]}",
            'type': 'Effective Date'
        })
    if record[2]:  # review_date
        calendar_data.append({
            'date': record[2].split()[0],  # Strip time part
            'event': f"Review Date of {record[0]}",
            'type': 'Review Date'
        })

calendar_df = pd.DataFrame(calendar_data)

# Streamlit UI
st.title('Governance Calendar')
st.sidebar.title('Upcoming Events')

# Display upcoming events in the sidebar
st.sidebar.write(upcoming_events)

# Calendar visualization
st.write("### Calendar with Important Dates")

def create_calendar(year, month, events):
    cal = calendar.Calendar(firstweekday=6)  # Sunday as the first day of the week

    # Create a DataFrame to hold the calendar data
    dates = []
    month_days = cal.monthdayscalendar(year, month)
    for week in month_days:
        for day in week:
            if day == 0:
                dates.append({'date': '', 'event': '', 'type': ''})
            else:
                event = events.get(day, '')
                dates.append({
                    'date': f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}",
                    'event': event['event'] if event else '',
                    'type': event['type'] if event else ''
                })

    calendar_df = pd.DataFrame(dates)

    # Create a Plotly figure
    fig = px.scatter(
        calendar_df,
        x=calendar_df.index % 7,
        y=calendar_df.index // 7,
        text='event',
        color='type',
        title=f'Important Dates in {calendar.month_name[month]} {year}',
        labels={'x': 'Day of Week', 'y': 'Week'}
    )

    # Update layout to look like a calendar
    fig.update_traces(marker=dict(size=20), selector=dict(mode='markers+text'))
    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=list(range(7)), ticktext=list(calendar.day_abbr)),
        yaxis=dict(tickmode='array', tickvals=list(range(len(month_days)))),
        showlegend=True,
        height=800,
        legend_title='Event Type',
        hoverlabel=dict(bgcolor='white', font_size=12, font_family='Arial'),
        hovermode='closest',
        margin=dict(l=50, r=50, t=50, b=50),
        template='plotly_white'
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(showgrid=False)

    return fig

# Prepare event data for the calendar
event_dict = {}
for _, row in calendar_df.iterrows():
    if row['date']:
        date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
        event_dict[date_obj.day] = {'event': row['event'], 'type': row['type']}

# Define default year and month
year = datetime.now().year
month = datetime.now().month

# Create and display the calendar
col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = st.columns(12)
with col1:
    if st.button('<<'):
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
with col2:
    if st.button('<'):
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
with col3:
    st.write(f'{calendar.month_name[month]} {year}')
with col4:
    if st.button('>'):
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
with col5:
    if st.button('>>'):
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

calendar_fig = create_calendar(year, month, event_dict)
st.plotly_chart(calendar_fig)

# Close the database connection
conn.close()
