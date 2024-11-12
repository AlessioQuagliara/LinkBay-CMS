from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time

def capture_screenshot(url, output_path):
    # opzioni di Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Esegui Chrome in modalità headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # driver di Chrome con le opzioni e il servizio
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Carica la pagina
    driver.get(url)
    time.sleep(3)

    # screenshot della pagina
    driver.save_screenshot('screenshot.png')

    # Elaborazione
    img = Image.open('screenshot.png')
    img.save(output_path)

    # Chiusura
    driver.quit()