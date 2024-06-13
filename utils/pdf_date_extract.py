import fitz  # PyMuPDF
import os
import re
import sqlite3
from datetime import datetime

# Get the absolute path to the root folder of your project
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Connect to the SQLite database (or create it if it doesn't exist)
db_path = os.path.join(root_path, 'users.db')
print(f"Database path: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create a table to store the governance information
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

def store_info(file_name, info):
    try:
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

def fetch_all_governance_records():
    cursor.execute('SELECT * FROM Governance')
    records = cursor.fetchall()
    return records

def fetch_all_dates():
    cursor.execute('SELECT date_effective, review_date FROM Governance')
    dates = cursor.fetchall()
    return dates

def fetch_events_for_date(target_date):
    target_date = datetime.strptime(target_date, '%d/%m/%Y').date()
    cursor.execute('''
    SELECT file_name, date_effective, review_date 
    FROM Governance 
    WHERE date_effective = ? OR review_date = ?
    ''', (target_date, target_date))
    events = cursor.fetchall()
    return events

def close_db_connection():
    conn.close()

# Directory containing PDFs
pdf_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pdfs')

if not os.path.exists(pdf_dir):
    print(f"The directory {pdf_dir} does not exist.")
else:
    for file_name in os.listdir(pdf_dir):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(pdf_dir, file_name)
            print(f"Processing {file_name}")
            governance_info = process_pdf(file_path)
            if governance_info:
                store_info(file_name, governance_info)
            else:
                print(f"Failed to extract governance info for {file_name}")

# Close the database connection
conn.close()
