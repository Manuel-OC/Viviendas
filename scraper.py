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
	options.headless = False
	options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

	driver = uc.Chrome(options=options, use_subprocess=True)
	return driver

def aceptar_cookies(driver):
	try:
		# Espera a que aparezca el banner de cookies (hasta 10 segundos)
		WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.ID, "didomi-notice"))
		)

		# Espera adicional de 2 segundos antes de interactuar
		time.sleep(2)

		# Espera a que el botón "Rechazar" esté visible y clickeable
		rechazar_btn = WebDriverWait(driver, 5).until(
			EC.element_to_be_clickable((By.ID, "didomi-notice-disagree-button"))
		)

		driver.execute_script("arguments[0].scrollIntoView(true);", rechazar_btn)

		# Mover el ratón y hacer clic
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
			driver.get(full_url)
			
			if pagina == 1:
				aceptar_cookies(driver)
			
			# Scroll lento con tiempo aleatorio
			for _ in range(5):
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(random.uniform(1.2, 2.5))
				WebDriverWait(driver, 10).until(
					EC.presence_of_element_located((By.CLASS_NAME, "item-price"))
				)

			if driver.current_url == url and nViviendas != 0:
				break

			print(f"Scrapeando {full_url}")

			soup = BeautifulSoup(driver.page_source, 'html.parser')
			precios = soup.find_all('span', class_='item-price')
			
			for precio in precios:
				texto = precio.get_text().strip().replace('.', '').replace('€', '').replace(',', '.')
				try:
					valor = float(re.findall(r'\d+(?:\.\d+)?', texto)[0])
					precioTotal += valor
					nViviendas += 1
				except (IndexError, ValueError):
					print(f"PROBLEMA EN LA URL {full_url} :'(")
					continue

			pagina += 1
			time.sleep(random.uniform(2, 5))  # Pausa entre páginas
		
		driver.quit()
		print(f"{nViviendas} encontradas!!")
		return precioTotal / nViviendas if nViviendas else 0

	except Exception as e:
		print(f"PROBLEMA EN LA URL {url} :'(")
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

	for i, ciudad in enumerate(ciudades):
		precio = scrape_url(ciudad)
		print(f"El precio medio de las viviendas en la URL {ciudad} es: {precio:.2f} €")

	ahora = datetime.now()
	fecha_hora_str = ahora.strftime("%Y-%m-%d %H:%M:%S")
	print(fecha_hora_str)  # Ej: "2025-06-21 23:52:12"

inicio()

