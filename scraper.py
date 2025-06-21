from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime

def obtener_precio_medio(url):
    options = Options()
    options.add_argument("--headless=new")  # modo headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")  # ocultar que es Selenium
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/114.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    # Agregar headers adicionales usando Chrome DevTools Protocol (CDP)
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': {
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br'
    }})

    try:
        print(f"Cargando página: {url}pagina-1.htm")
        driver.get(f"{url}pagina-1.htm")

        # Esperar hasta que aparezca un precio o timeout
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-price")))

        html = driver.page_source
        print(f"HTML cargado (primeros 1000 caracteres):\n{html[:1000]}")

        # Buscar todos los precios
        precios_elements = driver.find_elements(By.CLASS_NAME, "item-price")
        precios = []
        for elem in precios_elements:
            texto = elem.text.replace("€", "").replace(".", "").replace(",", ".").strip()
            try:
                precio = float(texto)
                precios.append(precio)
            except ValueError:
                continue

        print(f"Total viviendas encontradas: {len(precios)}")
        if precios:
            precio_medio = sum(precios) / len(precios)
        else:
            precio_medio = 0.0

        print(f"El precio medio de las viviendas en la URL {url} es: {precio_medio:.2f} €")

    except TimeoutException:
        print(f"Timeout esperando el elemento 'item-price'. La página puede no tener datos o estar bloqueada.")
        print(f"Total viviendas encontradas: 0")
        print(f"El precio medio de las viviendas en la URL {url} es: 0.00 €")

    finally:
        driver.quit()

if __name__ == "__main__":
    urls = [
        "https://www.idealista.com/venta-viviendas/chiclana-de-la-frontera-cadiz/",
        "https://www.idealista.com/venta-viviendas/cadiz-cadiz/",
        "https://www.idealista.com/venta-viviendas/puerto-real-cadiz/",
        "https://www.idealista.com/venta-viviendas/san-fernando-cadiz/"
    ]

    for url in urls:
        obtener_precio_medio(url)
    print("Fecha y hora de scraping:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
