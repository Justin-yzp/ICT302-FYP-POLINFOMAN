import streamlit as st
from streamlit_calendar import calendar
import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np


class Calendar:
    def __init__(self, db_path='users.db'):
        self.conn = sqlite3.connect(db_path)

    def fetch_all_dates(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT file_name, date_effective, review_date FROM Governance')
        all_dates = cursor.fetchall()
        return all_dates

    def fetch_upcoming_events(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT file_name, date_effective, review_date
        FROM Governance
        WHERE (strftime('%Y-%m-%d', date_effective) >= strftime('%Y-%m-%d', 'now')) 
           OR (strftime('%Y-%m-%d', review_date) >= strftime('%Y-%m-%d', 'now'))
        ''')
        upcoming_events = cursor.fetchall()
        return upcoming_events

    def prepare_data_for_calendar(self, all_dates):
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
        return calendar_events

    def fetch_pdfs_from_directory(self, directory='pdfs'):
        pdf_files = []
        if os.path.exists(directory) and os.path.isdir(directory):
            pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
        return pdf_files

    def close_connection(self):
        self.conn.close()

    def display_random_bar_chart(self):
        # Generate random data
        categories = ['A', 'B', 'C', 'D', 'E']
        values = np.random.randint(1, 100, size=5)

        # Create the bar chart with a transparent background
        fig, ax = plt.subplots(facecolor='none')
        bars = ax.bar(categories, values, color=(0, 0, 0, 0.6))  # Semi-transparent black bars

        # Customize the chart
        ax.set_facecolor('none')  # Transparent axes background
        ax.set_ylabel('Values', color=(0, 0, 0, 1))  # Solid black for ylabel
        ax.set_title('Random Bar Chart', color=(0, 0, 0, 1))  # Solid black for title
        ax.tick_params(colors=(0, 0, 0, 1))  # Solid black for tick labels

        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height}',
                    ha='center', va='bottom', color=(0, 0, 0, 1))  # Solid black for text

        # Make the spines (axis lines) black
        for spine in ax.spines.values():
            spine.set_color((0, 0, 0, 1))  # Solid black for spines

        # Adjust layout and display the chart
        plt.tight_layout()
        st.pyplot(fig, transparent=True)
    def display_calendar(self):
        all_dates = self.fetch_all_dates()
        upcoming_events = self.fetch_upcoming_events()
        calendar_events = self.prepare_data_for_calendar(all_dates)

        # Streamlit UI
        st.title('Governance Calendar')

        # Define layout columns
        col1, col2 = st.columns([3, 1])  # Adjusted column width

        # Left panel for placeholder (future graphs)
        with col1:
            st.write("### Sample Bar Chart")
            self.display_random_bar_chart()

        # Right panel for PDF listing
        with col2:
            st.title('PDF Files')
            pdf_files = self.fetch_pdfs_from_directory()
            for pdf_file in pdf_files:
                st.markdown(f"- {pdf_file}")

        # Horizontal line for separation
        st.markdown("---")

        # Centered container for Upcoming Events
        st.title('Upcoming Events')
        for event in upcoming_events:
            if event[1]:  # date_effective
                st.markdown(f"**Effective Date of {event[0]}**: {event[1]}")
            if event[2]:  # review_date
                st.markdown(f"**Review Date of {event[0]}**: {event[2]}")

        # Horizontal line for separation
        st.markdown("---")

        # Centered container for Calendar
        st.title('Calendar with Important Dates')
        try:
            calendar_component = calendar(events=calendar_events, options={
                'headerToolbar': {
                    'left': 'prev,next today',
                    'center': 'title',
                    'right': 'dayGridMonth,timeGridWeek,timeGridDay'
                },
                'initialView': 'dayGridMonth',
                'navLinks': True,
                'editable': True,
                'dayMaxEvents': True,
                'eventColor': '#378006'
            })
            # st.write(calendar_component)
        except Exception as e:
            st.error(f"Error rendering calendar: {str(e)}")

        self.close_connection()


# Usage
if __name__ == "__main__":
    cal = Calendar()
    cal.display_calendar()