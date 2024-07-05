import fitz  # PyMuPDF
import os
import re
import sqlite3
from datetime import datetime

def extract_governance_info(text):
    # Regular expressions to extract the required fields
    approval_authority = re.search(r'Approval Authority\s+(.*)', text)
    owner = re.search(r'Owner\s+(.*)', text)
    legislation = re.search(r'Legislation\s+mandating\s+compliance\s*(.*)', text)
    category = re.search(r'Category\s+(.*)', text)
    related_documents = re.search(r'Related University\s+Legislation\s+and\s+Policy\s+Documents\s+(.+?)(Date effective|Review date)', text, re.DOTALL)
    date_effective = re.search(r'Date effective\s+(\d{2}/\d{2}/\d{4})', text)
    review_date = re.search(r'Review date\s+(\d{2}/\d{2}/\d{4})', text)

    def get_value(match):
        return match.group(1).strip() if match and match.group(1).strip() else None

    return {
        'approval_authority': get_value(approval_authority),
        'owner': get_value(owner),
        'legislation': get_value(legislation),
        'category': get_value(category),
        'related_documents': get_value(related_documents),
        'date_effective': datetime.strptime(date_effective.group(1), '%d/%m/%Y') if date_effective else None,
        'review_date': datetime.strptime(review_date.group(1), '%d/%m/%Y') if review_date else None
    }

def process_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
        governance_info = extract_governance_info(text)
        return governance_info
    except Exception as e:
        print(f"Error processing PDF {file_path}: {e}")
        return None

def store_info(conn, file_name, info, failed_files):
    try:
        # Check if any required field is None
        if any(value is None for value in info.values()):
            print(f"Skipping {file_name} due to missing governance information.")
            failed_files.append(file_name)
            return

        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Governance (file_name, approval_authority, owner, legislation, category, related_documents, date_effective, review_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(file_name) DO UPDATE SET
            approval_authority=excluded.approval_authority,
            owner=excluded.owner,
            legislation=excluded.legislation,
            category=excluded.category,
            related_documents=excluded.related_documents,
            date_effective=excluded.date_effective,
            review_date=excluded.review_date
        ''', (
            file_name,
            info['approval_authority'],
            info['owner'],
            info['legislation'],
            info['category'],
            info['related_documents'],
            info['date_effective'],
            info['review_date']
        ))
        conn.commit()
        print(f"Successfully stored info for {file_name}")
    except Exception as e:
        print(f"Error storing info for {file_name}: {e}")
        failed_files.append(file_name)

def main():
    try:
        # Get the absolute path to the root folder of your project
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Connect to the SQLite database (or create it if it doesn't exist)
        db_path = os.path.join(root_path, 'users.db')
        print(f"Database path: {db_path}")
        conn = sqlite3.connect(db_path)

        # Create a table to store the governance information
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Governance (
            id INTEGER PRIMARY KEY,
            file_name TEXT UNIQUE,
            approval_authority TEXT,
            owner TEXT,
            legislation TEXT,
            category TEXT,
            related_documents TEXT,
            date_effective DATE,
            review_date DATE
        )
        ''')
        conn.commit()

        # Clear existing data in the Governance table
        cursor.execute('''DELETE FROM Governance''')
        conn.commit()

        # Directory containing PDFs
        pdf_dir = os.path.join(root_path, 'pdfs')

        if not os.path.exists(pdf_dir):
            print(f"The directory {pdf_dir} does not exist.")
            return []

        failed_files = []

        for file_name in os.listdir(pdf_dir):
            if file_name.endswith('.pdf'):
                file_path = os.path.join(pdf_dir, file_name)
                print(f"Processing {file_name}")
                governance_info = process_pdf(file_path)
                if governance_info:
                    store_info(conn, file_name, governance_info, failed_files)
                else:
                    failed_files.append(file_name)
                    print(f"Failed to extract governance info for {file_name}")

        # Close the database connection
        conn.close()

        # Return failed PDFs list
        return failed_files

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    failed_files = main()
    if failed_files:
        print("\nFailed to extract governance info for the following PDFs:")
        for file in failed_files:
            print(file)
    else:
        print("\nAll PDFs processed successfully.")
