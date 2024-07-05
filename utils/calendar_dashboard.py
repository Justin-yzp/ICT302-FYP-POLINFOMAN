import streamlit as st
from streamlit_calendar import calendar
import sqlite3
import os
import matplotlib.pyplot as plt
import sys
from streamlit_modal import Modal

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
        except Exception as e:
            st.error(f"Error updating categories and processing PDFs: {str(e)}")
            self.categories = {}

    def display_category_bar_chart(self):
        if not self.categories:
            st.warning("No categories available. Please update the dashboard.")
            return

        category_counts = {category: len(pdfs) for category, pdfs in self.categories.items()}
        categories = list(category_counts.keys())
        values = list(category_counts.values())

        fig, ax = plt.subplots(facecolor='none')
        bars = ax.bar(categories, values, color=(0, 0, 0, 0.6))  # Semi-transparent black bars

        ax.set_facecolor('none')  # Transparent axes background
        ax.set_ylabel('Number of PDFs', color=(0, 0, 0, 1))  # Solid black for ylabel
        ax.set_title('PDFs by Category', color=(0, 0, 0, 1))  # Solid black for title
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

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig, transparent=True)

    def display_calendar(self):
        st.title('Governance Calendar')

        col1, col2 = st.columns([5, 2])

        with col1:
            st.write("### PDFs by Category")
            self.display_category_bar_chart()

        with col2:
            st.title('PDF Files')
            selected_category = st.selectbox("Select a category", list(self.categories.keys()))

            # Add update dashboard button right below the dropdown
            if st.button('Update Dashboard'):
                self.update_categories()
                st.rerun()  # This will rerun the entire app

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

        # Display upcoming events and failed PDFs side by side with pagination
        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Upcoming Events')
            events_per_page = 2
            total_events = len(upcoming_events)
            max_events_page = (total_events - 1) // events_per_page

            start_idx = st.session_state.events_page * events_per_page
            end_idx = min(start_idx + events_per_page, total_events)

            for event in upcoming_events[start_idx:end_idx]:
                if event[1]:  # date_effective
                    st.write(f"**Effective Date of {os.path.splitext(event[0])[0]}**: {event[1].split()[0]}")
                if event[2]:  # review_date
                    st.write(f"**Review Date of {os.path.splitext(event[0])[0]}**: {event[2].split()[0]}")

            col1_1, col1_2 = st.columns(2)
            with col1_1:
                if st.button('Previous Events', key='prev_events', disabled=st.session_state.events_page == 0):
                    st.session_state.events_page = max(0, st.session_state.events_page - 1)
                    st.rerun()  # Rerun to update the display
            with col1_2:
                if st.button('Next Events', key='next_events',
                             disabled=st.session_state.events_page == max_events_page):
                    st.session_state.events_page = min(max_events_page, st.session_state.events_page + 1)
                    st.rerun()  # Rerun to update the display

        with col2:
            st.subheader('Outdated PDF Format')
            pdfs_per_page = 5
            total_pdfs = len(self.failed_pdfs)
            max_pdfs_page = (total_pdfs - 1) // pdfs_per_page

            start_idx = st.session_state.failed_pdfs_page * pdfs_per_page
            end_idx = min(start_idx + pdfs_per_page, total_pdfs)

            if self.failed_pdfs:
                for pdf in self.failed_pdfs[start_idx:end_idx]:
                    st.write(f"- {pdf}")
            else:
                st.write("No PDFs failed to process.")

            col2_1, col2_2 = st.columns(2)
            with col2_1:
                if st.button('Previous PDFs', key='prev_pdfs', disabled=st.session_state.failed_pdfs_page == 0):
                    st.session_state.failed_pdfs_page = max(0, st.session_state.failed_pdfs_page - 1)
                    st.rerun()  # Rerun to update the display
            with col2_2:
                if st.button('Next PDFs', key='next_pdfs', disabled=st.session_state.failed_pdfs_page == max_pdfs_page):
                    st.session_state.failed_pdfs_page = min(max_pdfs_page, st.session_state.failed_pdfs_page + 1)
                    st.rerun()  # Rerun to update the display

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