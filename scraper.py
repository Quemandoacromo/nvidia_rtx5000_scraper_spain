import os
# Disable messages
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import subprocess
import platform
import time
import json
import re
from datetime import datetime

# Lista de dependencias necesarias (mapeo de nombres para instalación e importación)
required_packages = [
    "setuptools",
    "pygame",
    "selenium",
    "beautifulsoup4",
    "undetected_chromedriver"
]

# Constants
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'  # Para restaurar el color predeterminado
SOUND_FILE = 'src/sounds/found.mp3'

# Rutas de los diccionarios
TARGETS_FILE = "src/data/targets.json"
TEST_TARGETS_FILE = "src/data/test_targets.json"


# Functions
def log_product_found(url):
    """Log the URL and current local time when a product is found."""
    with open("series_50_disponibles.txt", "a") as file:
        file.write(f"URL: {url} - Found at {current_time()}\n")

def current_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_time

def print_separator(width=100):
    print('\n' + '='.center(width, '=') + '\n')

def install_packages(packages):
    """Instala paquetes si no están disponibles."""
    import sys
    print(f"📦 Reconstituyendo distutils...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", "setuptools"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,  # Oculta salida
    )
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"📦 Instalando {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def show_menu():
    print_separator()
    print("🎯 Selecciona una opción:")
    print("1️🔹 Empezar Búsqueda")
    print("2️🔹 Modo Test de URLs")
    print("3️🔹 Salir")
    print(f"\n\tScript desarrollado por: {RED}RealMaxPump {RESET}")
    print("\thttps://github.com/realmaxpump")
    print_separator()

def load_urls_from_file(file):
    try:
        with open(file, "r", encoding="utf-8") as file:
            return json.load(file)  # Carga el archivo como un diccionario JSON
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error al cargar el archivo {file}: {e}")
        return {}

def get_chrome_version():
    """Obtiene la versión instalada de Chrome en Windows, Linux o macOS."""
    try:
        system = platform.system().lower()  # Obtener el sistema operativo

        if system == "windows":
            # Comando para obtener la versión de Chrome en Windows
            result = subprocess.run(
                ["reg", "query", "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon", "/v", "version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                # Extraer la versión de la salida del comando
                version = result.stdout.strip().split()[-1]
                return int(version.split(".")[0])  # Devolver solo el número principal (por ejemplo, 133)
            else:
                print("❌ No se pudo obtener la versión de Chrome en Windows.")
                return None

        elif system == "linux":
            # Comando para obtener la versión de Chrome en Linux
            result = subprocess.run(
                ["google-chrome", "--version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                # Extraer la versión de la salida del comando
                version = re.search(r"\d+\.\d+\.\d+", result.stdout.strip())
                if version:
                    return int(version.group().split(".")[0])  # Devolver solo el número principal
            else:
                print("❌ No se pudo obtener la versión de Chrome en Linux.")
                return None

        elif system == "darwin":  # macOS
            # Comando para obtener la versión de Chrome en macOS
            result = subprocess.run(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                # Extraer la versión de la salida del comando
                version = re.search(r"\d+\.\d+\.\d+", result.stdout.strip())
                if version:
                    return int(version.group().split(".")[0])  # Devolver solo el número principal
            else:
                print("❌ No se pudo obtener la versión de Chrome en macOS.")
                return None

        else:
            print(f"❌ Sistema operativo no compatible: {system}")
            return None

    except Exception as e:
        print(f"❌ Error al obtener la versión de Chrome: {e}")
        return None

def check_availability(url, search_terms):
    """Verifica la disponibilidad de las tarjetas gráficas en la página, ignorando header, footer, scripts y metadatos."""
    try:
        driver.get(url)  # Intentar cargar la página con timeout de 15 segundos
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Esperar hasta que la página cargue completamente (máximo 10 segundos)
        WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.CSS_SELECTOR, "main, body")))

        try:
            page_element = driver.find_element(By.TAG_NAME, "main")
        except:
            # Si no hay <main>, extraer contenido de <body>
            page_element = driver.find_element(By.TAG_NAME, "body")

        # Eliminar elementos no deseados directamente del DOM
        tags_to_remove = ["header", "footer", "script", "style", "meta", "nav", "aside"]
        for tag in tags_to_remove:
            driver.execute_script(f"""
                var elements = document.getElementsByTagName('{tag}');
                while (elements[0]) {{
                    elements[0].parentNode.removeChild(elements[0]);
                }}
            """)

        # Obtener el contenido filtrado
        page_content = page_element.get_attribute("innerHTML")

        # Utilizamos BeautifulSoup para limpiar y extraer solo el texto visible
        soup = BeautifulSoup(page_content, 'html.parser')

        # Obtener el texto visible (sin etiquetas de estilo, script, etc.)
        visible_text = ' '.join(soup.stripped_strings)

        # Expresión regular para buscar los textos sin distinguir mayúsculas/minúsculas
        found = False
        for term in search_terms:
            # Revisar si el término está presente en el texto visible
            if re.search(rf"\b{re.escape(term)}\b", visible_text, re.IGNORECASE):
                found = True
                #print(f"Término encontrado: {term}")  # Muestra el término que se encontró
                break
        if found:
            try:
                money.play()
            except Exception as e:
                print(f"❌ No se ha podido reproducir la alarma: {e}")

            log_product_found(url)
            print_separator()
            print(f"💸💸💸💸 PRODUCTO DISPONIBLE  💸💸💸💸")
            print(f"\n{url}")
            print_separator()
        else:
            short_url = url[:70] + "..." if len(url) > 70 else url
            print(f"❌ Producto NO disponible en: {short_url}")

    except Exception as e:
        print(f"⚠️ Error al procesar {url}: {e}")


#####################################
########### Execution ###############
#####################################

# Instalar e importar librerías
install_packages(required_packages)

import pygame
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


print("✅ Todas las dependencias han sido instaladas e importadas correctamente.")

# Configure Chrome options. Obfuscate identity to bypass antibot measures
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--headless=new")  # Modo completamente oculto
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--enable-unsafe-webgl")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--use-gl=swiftshader")


# Detectar la versión de Chrome instalada
chrome_version = get_chrome_version()

# Inicializar WebDriver
if chrome_version:
    print(f"✅ Versión de Chrome detectada: {chrome_version}")
    try:
        driver = uc.Chrome(version_main=chrome_version, use_subprocess=True, options=chrome_options)
        driver.set_page_load_timeout(15)  # Timeout de carga de página: 15 segundos
    except Exception as e:
        print(f"❌ Error al iniciar WebDriver: {e}")
        exit()
else:
    print(f"❌ Ejecutando driver de manera genérica")
    try:
        driver = uc.Chrome(use_subprocess=True, options=chrome_options)
        driver.set_page_load_timeout(15)  # Timeout de carga de página: 15 segundos
    except Exception as e:
        print(f"❌ Error al iniciar WebDriver: {e}")
        exit()

# Inicializar Alarma
pygame.init()
if not os.path.isfile(SOUND_FILE):
    print(f"⚠️ El archivo de sonido no se encuentra en la ruta: {SOUND_FILE}")
else:
    money = pygame.mixer.Sound(SOUND_FILE)
    print(f"✅ 🚨Alarma🚨 preparada")

while True:
    show_menu()
    choice = input("🔹 Opción (1/2/3): ").strip()

    if choice == "1":
        print("\n🚀 Iniciando búsqueda de disponibilidad...")
        urls_with_terms = load_urls_from_file(TARGETS_FILE)
        break
    elif choice == "2":
        print("\n🛠️ Iniciando Modo Test con URLs de prueba...")
        urls_with_terms = load_urls_from_file(TEST_TARGETS_FILE)
        break
    elif choice == "3":
        print("👋 ¡Espero que haya habido suerte!")
        sys.exit()
    else:
        print("❌ Opción inválida. Inténtalo de nuevo.")

# Loop infinito para revisar cada página periódicamente
try:
    while True:
        for url, search_terms in urls_with_terms.items():
            check_availability(url, search_terms)
        print("\n🔄 Esperando antes de la próxima revisión... 🔄\n")
        time.sleep(2)

except KeyboardInterrupt:
    print("\n❌ Búsqueda detenida manualmente.")
    driver.quit()
