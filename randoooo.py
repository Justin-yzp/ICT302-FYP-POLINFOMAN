import os
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

def get_document_title(driver):
    try:
        title_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="document-title"]'))
        )
        return title_element.text.strip()
    except TimeoutException:
        return "Untitled_Document"

def save_as_pdf(url, output_directory, edge_driver_path):
    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_argument("--headless")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")

    prefs = {
        'printing.print_preview_sticky_settings.appState': '{"recentDestinations":[{"id":"Save as PDF","origin":"local","account":"","capabilities":{}}],"selectedDestinationId":"Save as PDF","version":2}',
        'savefile.default_directory': output_directory
    }
    edge_options.add_experimental_option('prefs', prefs)

    try:
        service = Service(edge_driver_path)
        driver = webdriver.Edge(service=service, options=edge_options)

        driver.get(url)

        title = get_document_title(driver)
        safe_title = "".join([c if c.isalnum() else "_" for c in title])
        output_path = os.path.join(output_directory, f'{safe_title}.pdf')

        try:
            print_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="print-button"]'))
            )
            print_button.click()

            time.sleep(5)

            print(f'Saved {url} as {output_path}')
        except TimeoutException:
            print(f"Print button not found for {url}")

    except WebDriverException as e:
        print(f"WebDriverException: {e}")

    finally:
        driver.quit()

def download_documents(url_list, output_directory, edge_driver_path):
    os.makedirs(output_directory, exist_ok=True)

    for url in url_list:
        save_as_pdf(url, output_directory, edge_driver_path)

if __name__ == "__main__":
    urls = [
        "https://murdoch.navexone.com/content/dotNet/documents/?docid=3228&public=true",
        # Add more URLs here
    ]
    output_dir = "output_pdfs"
    edge_driver_path = r"C:\Users\zhanp\Downloads\edgedriver_win64\msedgedriver.exe"
    download_documents(urls, output_dir, edge_driver_path)