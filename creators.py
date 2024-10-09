from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time

def capture_screenshot(url, output_path):
    # Imposta le opzioni di Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Esegui Chrome in modalità headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Avvia il driver di Chrome con le opzioni e il servizio
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Carica la pagina da cui vuoi catturare uno screenshot
    driver.get(url)

    # Aspetta che la pagina sia completamente caricata
    time.sleep(3)

    # Fai uno screenshot della pagina
    driver.save_screenshot('screenshot.png')

    # Elabora lo screenshot se necessario
    img = Image.open('screenshot.png')
    img.save(output_path)

    # Chiudi il driver
    driver.quit()