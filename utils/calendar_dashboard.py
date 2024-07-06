from datetime import datetime

import streamlit as st
from streamlit_calendar import calendar
import sqlite3
import os
import matplotlib.pyplot as plt
import sys
from streamlit_modal import Modal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add the utils folder to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

# Import the categorize_pdfs function
from categorize_pdfs import categorize_pdfs
from pdf_date_extract import main as process_pdfs_main


class Calendar:
    def __init__(self, db_path='users.db', categories_file='categorized_pdfs.txt', failed_pdfs_file='failed_pdfs.txt'):
        self.conn = sqlite3.connect(db_path)
        self.categories_file = categories_file
        self.failed_pdfs_file = failed_pdfs_file
        self.categories = self.load_categories()
        self.failed_pdfs = self.load_failed_pdfs()
        if not self.categories:
            self.update_categories()

        # Initialize session state for pagination
        if 'events_page' not in st.session_state:
            st.session_state.events_page = 0
        if 'failed_pdfs_page' not in st.session_state:
            st.session_state.failed_pdfs_page = 0

    def load_failed_pdfs(self):
        if os.path.exists(self.failed_pdfs_file):
            with open(self.failed_pdfs_file, 'r') as f:
                return [line.strip() for line in f.readlines()]
        return []

    def load_categories(self):
        if os.path.exists(self.categories_file):
            with open(self.categories_file, 'r') as f:
                categories = {}
                current_category = None
                for line in f:
                    line = line.strip()
                    if line.endswith(':'):
                        current_category = line[:-1]
                        categories[current_category] = []
                    elif line.startswith('- ') and current_category:
                        pdf_name = line[2:]
                        categories[current_category].append(pdf_name)
                return categories
        return None

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

    def update_categories(self):
        try:
            categorize_pdfs()
            self.categories = self.load_categories()
            if self.categories:
                st.success('Categories updated successfully!')
            else:
                st.error('Failed to load categories after update.')

            # Run the process_pdfs_main function
            process_pdfs_main()
            # Reload the failed PDFs
            self.failed_pdfs = self.load_failed_pdfs()
            if self.failed_pdfs:
                st.warning(f"Failed to process {len(self.failed_pdfs)} PDFs.")
            else:
                st.success('All PDFs processed successfully!')

            # Fetch updated dates after processing PDFs
            self.fetch_all_dates()
            self.fetch_upcoming_events()

        except Exception as e:
            st.error(f"Error updating categories and processing PDFs: {str(e)}")
            self.categories = {}

    def display_category_pie_chart(self):
        if not self.categories:
            st.warning("No categories available. Please update the dashboard.")
            return

        category_counts = {category: len(pdfs) for category, pdfs in self.categories.items()}
        categories = list(category_counts.keys())
        values = list(category_counts.values())

        fig, ax = plt.subplots(figsize=(10, 8), facecolor='none')

        # Define colors
        colors = ['#8e44ad', '#e74c3c', '#3498db', '#2ecc71', '#f39c12']

        # Create pie chart
        wedges, texts, autotexts = ax.pie(values, labels=None, autopct='%1.1f%%',
                                          startangle=90, colors=colors, pctdistance=0.85)

        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')

        # Add lines and labels
        bbox_props = dict(boxstyle="round,pad=0.3", fc="w", ec="k", lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle="-", color="k"),
                  bbox=bbox_props, zorder=0, va="center")

        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate(categories[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                        horizontalalignment=horizontalalignment, **kw)

        ax.set_title('PDFs by Category', fontsize=16, fontweight='bold')

        # Remove duplicated text inside pie slices
        for autotext in autotexts:
            autotext.set_visible(False)

        # Add a legend
        ax.legend(wedges, categories, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        plt.tight_layout()
        st.pyplot(fig, transparent=True)

    def display_calendar(self):
        st.title('Governance Calendar')

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write("### PDFs by Category")
            self.display_category_pie_chart()

        with col2:
            st.title('PDF Files')
            selected_category = st.selectbox("Select a category", list(self.categories.keys()))

            # Add update dashboard button right below the dropdown
            if st.button('Update Dashboard'):
                self.update_categories()
                st.experimental_rerun()  # This will rerun the entire app

        # Fetch data after potential update
        all_dates = self.fetch_all_dates()
        upcoming_events = self.fetch_upcoming_events()
        calendar_events = self.prepare_data_for_calendar(all_dates)

        st.markdown("---")

        # New section for displaying PDF files
        if selected_category:
            st.write(f"### PDFs in {selected_category}")
            pdf_cols = st.columns(3)  # Create 3 columns for PDF names
            for i, pdf_file in enumerate(self.categories[selected_category]):
                pdf_name = os.path.splitext(pdf_file)[0]
                pdf_cols[i % 3].write(pdf_name)

        st.markdown("---")

        # Create a combined dataframe for upcoming events and outdated PDFs
        events_data = []
        today = datetime.today().date()

        for event in upcoming_events:
            review_date = datetime.strptime(event[2].split()[0], '%Y-%m-%d').date() if event[2] else None
            remarks = 'Upcoming Event' if review_date and review_date >= today else 'Expired PDF'
            events_data.append({
                'File Name': os.path.splitext(event[0])[0],
                # 'Effective Date': event[1].split()[0] if event[1] else '',
                'Review Date': event[2].split()[0] if event[2] else '',
                'Remarks': remarks
            })

        for pdf in self.failed_pdfs:
            events_data.append({
                'File Name': os.path.splitext(pdf)[0],
                # 'Effective Date': '',
                'Review Date': '',
                'Remarks': 'Outdated Format'
            })

        df = pd.DataFrame(events_data)

        # Display the combined table
        st.subheader('Upcoming Events and Outdated PDFs')

        # Add checkbox for filtering
        show_upcoming_events = st.checkbox('Show Upcoming Events', value=True)
        show_outdated_pdfs = st.checkbox('Show Outdated PDFs', value=True)
        show_expired_pdfs = st.checkbox('Show Expired PDFs', value=True)

        # Filter data based on checkboxes
        if not show_upcoming_events:
            df = df[df['Remarks'] != 'Upcoming Event']
        if not show_outdated_pdfs:
            df = df[df['Remarks'] != 'Outdated Format']
        if not show_expired_pdfs:
            df = df[df['Remarks'] != 'Expired PDF']

        # Display the table with a scroll bar
        st.dataframe(df, height=400)

        st.markdown("---")

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