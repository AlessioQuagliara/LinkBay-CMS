from selenium import webdriver
from PIL import Image
import time

def capture_screenshot(url, output_path):
    # Imposta il driver di Selenium (ad esempio, ChromeDriver)
    driver = webdriver.Chrome()  # Assicurati che ChromeDriver sia nel PATH

    # Carica la pagina da cui vuoi catturare uno screenshot
    driver.get(url)

    # Aspetta che la pagina sia completamente caricata
    time.sleep(3)

    # Fai uno screenshot della pagina
    driver.save_screenshot('screenshot.png')

    # Elabora lo screenshot se necessario
    img = Image.open('screenshot.png')
    img = img.crop((0, 0, 1200, 800))  # Taglia l'immagine se necessario
    img.save(output_path)

    # Chiudi il driver
    driver.quit()

# Cattura uno screenshot della route '/'
capture_screenshot('http://127.0.0.1:5000/', 'screenshot_result.png')

# Se vuoi catturare uno screenshot ogni 5 minuti, puoi impostare un ciclo:
while True:
    capture_screenshot('http://127.0.0.1:5000/', 'screenshot_result.png')
    time.sleep(3)  # Attendi 5 minuti (300 secondi)