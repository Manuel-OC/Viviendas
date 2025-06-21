import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import random
from selenium.webdriver import ActionChains
from datetime import datetime

def crear_driver():
	options = uc.ChromeOptions()
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	options.add_argument("--window-size=1920,1080")
	options.add_argument("--lang=es-ES")
	options.headless = False  # <-- Modo visible para depurar
	options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")
	options.add_argument("--disable-blink-features=AutomationControlled")
	driver = uc.Chrome(options=options, use_subprocess=True)
	return driver

def aceptar_cookies(driver):
	try:
		WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, "didomi-notice"))
		)
		time.sleep(2)
		rechazar_btn = WebDriverWait(driver, 5).until(
			EC.element_to_be_clickable((By.ID, "didomi-notice-disagree-button"))
		)
		driver.execute_script("arguments[0].scrollIntoView(true);", rechazar_btn)
		ActionChains(driver).move_to_element(rechazar_btn).click().perform()
		print("Botón 'Rechazar' clicado correctamente.")
	except Exception as e:
		print(f"No se pudo hacer clic en 'Rechazar': {e}")

def scrape_url(url):
	try:
		pagina = 1
		nViviendas = 0
		precioTotal = 0
		driver = crear_driver()

		while True:
			full_url = f"{url}pagina-{pagina}.htm"
			print(f"\nCargando página: {full_url}")
			driver.get(full_url)

			# Imprimir los primeros 1000 caracteres del HTML para diagnóstico
			html_snippet = driver.page_source[:1000]
			print("HTML cargado (primeros 1000 caracteres):")
			print(html_snippet)

			# Esperar a que cargue el primer precio o timeout en 15 seg
			try:
				WebDriverWait(driver, 15).until(
					EC.presence_of_element_located((By.CLASS_NAME, "item-price"))
				)
			except Exception:
				print("Timeout esperando el elemento 'item-price'. La página puede no tener datos o estar bloqueada.")
				break

			if pagina == 1:
				aceptar_cookies(driver)

			# Scroll lento con tiempo aleatorio para cargar elementos lazy-load
			for _ in range(5):
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(random.uniform(1.2, 2.5))

			# Volver a obtener el html tras scroll
			soup = BeautifulSoup(driver.page_source, 'html.parser')
			precios = soup.find_all('span', class_='item-price')

			if not precios:
				print("No se encontraron precios en esta página, finalizando scraping.")
				break

			for precio in precios:
				texto = precio.get_text().strip().replace('.', '').replace('€', '').replace(',', '.')
				try:
					valor = float(re.findall(r'\d+(?:\.\d+)?', texto)[0])
					precioTotal += valor
					nViviendas += 1
				except (IndexError, ValueError):
					print(f"PROBLEMA al convertir precio: '{texto}' en la URL {full_url} :'(")
					continue

			pagina += 1
			time.sleep(random.uniform(2, 5))  # Pausa entre páginas

		driver.quit()
		print(f"\nTotal viviendas encontradas: {nViviendas}")
		return precioTotal / nViviendas if nViviendas else 0

	except Exception as e:
		print(f"PROBLEMA GENERAL EN LA URL {url} :'(")
		print(e)
		try:
			driver.quit()
		except:
			pass
		return 0

def inicio():
	ciudades = [
		'https://www.idealista.com/venta-viviendas/chiclana-de-la-frontera-cadiz/',
		'https://www.idealista.com/venta-viviendas/cadiz-cadiz/',
		'https://www.idealista.com/venta-viviendas/puerto-real-cadiz/',
		'https://www.idealista.com/venta-viviendas/san-fernando-cadiz/'
	]

	for ciudad in ciudades:
		precio = scrape_url(ciudad)
		print(f"\nEl precio medio de las viviendas en la URL {ciudad} es: {precio:.2f} €")

	ahora = datetime.now()
	fecha_hora_str = ahora.strftime("%Y-%m-%d %H:%M:%S")
	print(f"\nFecha y hora de scraping: {fecha_hora_str}")

if __name__ == "__main__":
	inicio()
