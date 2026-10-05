import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc 
import time

def extract_IDs(
        sleep_time : int = 2,
        verbose : bool = True
) -> list:
    """
    Extrae el ID de los inmuebles de todas las páginas posibles.
     
    :param sleep_time: tiempo de espera para pasar desapercibido
    :param verbose: indica si se necesita proporcionar información del proceso
    :returns IDs: lista con el ID de todos los inmuebles 
    """
    driver = uc.Chrome()
    page = 1
    errors = 0
    ids = []
    print("Extrayendo IDs....")
    while True:
        if errors == 3:
            print("Han habido 3 errores seguidos, por lo que se detiene el proceso")
            break
        try:
            # Obtiene URL de la página actual
            url = f"https://www.idealista.com/venta-viviendas/santa-cruz-de-tenerife-santa-cruz-de-tenerife/pagina-{page}.htm"
            driver.get(url = url)

            time.sleep(sleep_time)

            # Busca el botón de aceptar cookies, y hace click si lo encuentra
            try:
                button = driver.find_element(By.XPATH, '//*[@id="didomi-notice-agree-button"]')
                button.click()
            except:
                pass

            time.sleep(sleep_time)

            # Obtenemos el HTML parseado para poder buscar
            html = driver.page_source
            parser = BeautifulSoup(html, "html.parser")

            articles = parser.find("main", attrs = {"id" : "main-content"}).find_all("article")
            real_page = parser.find("li", attrs = {"class" : "selected"}).find("span").text
            real_page = int(real_page)

            if page != real_page:
                break

            num = 0
            for article in articles:
                try:
                    attrs = article.attrs
                    assert "data-element-id" in attrs
                    id = attrs["data-element-id"]
                    ids.append(id)
                    num += 1
                except AssertionError:
                    continue
            print(f"Página {real_page} => {num} IDs extraídas | Acumulado => {len(ids)}")

            page += 1

        except Exception as e:
            print(f"Error en la página {page}: {e}")
            errors += 1
            continue

    driver.close()
    return ids

def extract_features(
        ids : list,
        sleep_time : int,
        json_path : str = None,
        error_verbose : bool = False
) -> dict:
    """
    Extrae características de los pisos, entre las que se encuentran:

        · Título de la oferta
        · Precio del inmueble
        · Localización
        · Otras características a limpiar

    
    :param ids: lista con el ID de los inmuebles
    :param sleep_time: tiempo de espera para pasar desapercibido
    :param json_name: ruta del archivo json, no se guarda si no se da
    :param error_verbose: indicar o no información sobre errores
    :returns cs: diccionario con las características de los distintos inmuebles
    """
    cs = {}
    driver = uc.Chrome()
    errors = 0
    for i, id in enumerate(ids):
        if errors == 3:
            print("Han habido 3 errores consecutivos, por lo que se cancela el proceso.")
            break

        url = f"https://www.idealista.com/inmueble/{id}/"
        driver.get(url)
        
        time.sleep(sleep_time)

        try:
            button = driver.find_element(By.XPATH, '//*[@id="didomi-notice-agree-button"]')
            button.click()
        except:
            pass
        
        time.sleep(sleep_time)

        html = driver.page_source
        parser = BeautifulSoup(html, "html.parser")

        try:
            title = parser.find("h1").find("span").text
            location = parser.find("span", {"class" : "main-info__title-minor"}).text.split(",")[0].strip()
            price = parser.find("span", {"class" : "txt-bold"}).text.replace(".", "")
            price = int(price)
            basic_features = parser.find("div", {"class" : "details-property-feature-one"})
            lis = basic_features.find_all("li")
            feats = [li.text.strip() for li in lis]
            errors = 0
        except Exception as e:
            print(f"Error at ID {id}: {e}")
            errors += 1
            continue

        features = {
            "titulo" : title,
            "precio" : price,
            "ubicacion" : location,
            "caracteristicas" : feats
        }


        cs[id] = features

        if i % 10 == 0:
            print(f"Features extracted from {i} IDs", end = "\r")
    
    if type(json_path) == str:
        json_path = json_path[:-5] + "_interrupted.json" if errors == 3 else json_path
        df = pd.DataFrame.from_dict(cs).T
        df.to_json(json_path)
    
    driver.close()
    return cs