import os
import logging

import openai
from openai import OpenAI
from time import sleep
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


openai.api_key = st.secrets.openai_key
client = OpenAI(api_key=openai.api_key)


def retry_with_exponential_backoff(
        func,
        max_retries=5,
        initial_delay=1,
        exponential_base=2,
        errors=(Exception,),
):
    def wrapper(*args, **kwargs):
        delay = initial_delay
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except errors as e:
                if i == max_retries - 1:
                    raise
                logging.warning(f"Attempt {i + 1} failed: {str(e)}. Retrying in {delay} seconds.")
                sleep(delay)
                delay *= exponential_base

    return wrapper


@retry_with_exponential_backoff
def categorize_pdf_names(pdf_names):
    prompt = (
            "You are an expert in university document classification. Categorize the following PDF names into these categories: "
            "Governance, Health Safety and Environment, Learning and Teaching, Physical Facilities, Research.\n\n"
            "Use the following guidelines:\n"
            "- Governance: policies related to university administration, ethics, and overall management.\n"
            "- Health Safety and Environment: policies about health, safety, sustainability, and environmental issues.\n"
            "- Learning and Teaching: policies about academic programs, assessments, and student-related matters.\n"
            "- Physical Facilities: policies about university buildings, spaces, and physical resources.\n"
            "- Research: policies about research conduct, data management, and research-related procedures.\n\n"
            "Format the response exactly as follows:\n"
            "Governance:\n- PDF name\n...\n"
            "Health Safety and Environment:\n- PDF name\n...\n"
            "Learning and Teaching:\n- PDF name\n...\n"
            "Physical Facilities:\n- PDF name\n...\n"
            "Research:\n- PDF name\n...\n\n"
            "PDF Names to categorize:\n"
            + "\n".join(pdf_names)
    )

    logging.info("Sending prompt to OpenAI")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Using GPT-4 for improved accuracy
        messages=[
            {"role": "system",
             "content": "You are a highly accurate assistant that categorizes university policy PDF names."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    logging.info("Received response from OpenAI")

    categorized_pdfs = response.choices[0].message.content
    return categorized_pdfs.strip().split('\n')


def get_pdf_files(directory):
    if os.path.exists(directory) and os.path.isdir(directory):
        pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
        logging.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files
    else:
        logging.error(f"Directory {directory} does not exist or is not a directory.")
        return []


def process_categories(categories):
    categorized_dict = {
        "Governance": [],
        "Health Safety and Environment": [],
        "Learning and Teaching": [],
        "Physical Facilities": [],
        "Research": []
    }

    current_category = None
    for line in categories:
        line = line.strip()
        if line.endswith(':'):
            current_category = line[:-1]
        elif line.startswith('- ') and current_category:
            pdf_name = line[2:]
            if current_category in categorized_dict:
                categorized_dict[current_category].append(pdf_name)

    return categorized_dict


def save_categorization_to_file(categorized_dict, file_path):
    with open(file_path, 'w') as f:
        for category, pdf_list in categorized_dict.items():
            f.write(f"\n{category}:\n")
            if pdf_list:
                for pdf in pdf_list:
                    f.write(f"  - {pdf}\n")
            else:
                f.write("  No PDFs in this category.\n")


def categorize_pdfs():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_directory = os.path.join(script_dir, '..', 'pdfs')
    output_file = os.path.join(script_dir, '..', 'categorized_pdfs.txt')

    pdf_files = get_pdf_files(pdf_directory)

    if pdf_files:
        categories = categorize_pdf_names(pdf_files)
        categorized_dict = process_categories(categories)

        logging.info("Saving categorized PDFs to file")
        save_categorization_to_file(categorized_dict, output_file)

        logging.info("PDF Categorization saved to file successfully")
    else:
        logging.warning("No PDF files found in the directory.")


if __name__ == "__main__":
    categorize_pdfs()
