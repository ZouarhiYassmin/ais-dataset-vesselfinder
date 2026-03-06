import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re
import time
import logging

# ----- CONFIGURATION LOGGING -----
logging.basicConfig(
    filename="ais_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ----- LISTE DES BATEAUX -----
vessels = {
    "CARITA": "https://www.vesselfinder.com/fr/vessels/details/9993042",
    "SY_TICONDEROGA": "https://www.vesselfinder.com/fr/vessels/details/367384280",
    "FORTUNATE_SUN": "https://www.vesselfinder.com/fr/vessels/details/1008243",
    "GULDEN_LEEUW": "https://www.vesselfinder.com/fr/vessels/details/5085897",
    "RISING_SUN": "https://www.vesselfinder.com/fr/vessels/details/8982307",
    "ARROW": "https://www.vesselfinder.com/fr/vessels/details/9970337",
    "PANTHALASSA": "https://www.vesselfinder.com/fr/vessels/details/9578103",
    "FRYDERYK_CHOPIN": "https://www.vesselfinder.com/fr/vessels/details/9030747"
}

data_folder = "data"
os.makedirs(data_folder, exist_ok=True)

# ----- EXTRACTION NOMBRE -----
def extract_number(text):
    if text is None:
        return None
    text = text.replace(",", ".")
    match = re.search(r"[-+]?\d*\.\d+|\d+", text)
    return float(match.group()) if match else None

# ----- SCRAPER DONNÉES -----
def get_vessel_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur connexion pour {url}: {e}")
        return None

    if "VesselFinder" not in response.text:
        logging.warning(f"Page bloquée ou HTML inattendu pour {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    data = {}

    ship_name = soup.find("h1")
    data["ship_name"] = ship_name.text.strip() if ship_name else "Unknown"

    rows = soup.find_all("tr")
    if not rows:
        logging.warning(f"Aucune ligne <tr> trouvée pour {data['ship_name']}")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 2:
            key = cols[0].text.strip()
            value = cols[1].text.strip()
            data[key] = value

    data["timestamp"] = datetime.utcnow()

    # Extraction position depuis les clés du tableau (FR/EN)
    position = (
        data.get("Position") or
        data.get("Coordinates") or
        data.get("Coordonnées") or
        ""
    )
    if "/" in position:
        parts = position.split("/")
        data["latitude"] = extract_number(parts[0])
        data["longitude"] = extract_number(parts[1])
    else:
        # Cherche les coordonnées directement dans le HTML brut
        coord_match = re.search(
            r'([-+]?\d{1,3}\.\d+)\s*/\s*([-+]?\d{1,3}\.\d+)',
            response.text
        )
        if coord_match:
            data["latitude"] = float(coord_match.group(1))
            data["longitude"] = float(coord_match.group(2))
        else:
            # Cherche dans les meta tags ou JSON embarqué
            lat_match = re.search(r'"latitude"\s*:\s*([-+]?\d+\.\d+)', response.text)
            lon_match = re.search(r'"longitude"\s*:\s*([-+]?\d+\.\d+)', response.text)
            data["latitude"] = float(lat_match.group(1)) if lat_match else None
            data["longitude"] = float(lon_match.group(1)) if lon_match else None

    # Extraction vitesse et cap (FR/EN)
    speed_val = (
        data.get("Speed") or
        data.get("Vitesse") or
        data.get("Direction / Vitesse") or
        ""
    )
    course_val = (
        data.get("Course") or
        data.get("Cap") or
        data.get("Direction") or
        ""
    )
    data["speed"] = extract_number(speed_val)
    data["course"] = extract_number(course_val)

    logging.info(f"Données récupérées pour {data['ship_name']}")
    return data

# ----- SCRIPT PRINCIPAL -----
def main():
    logging.info("Démarrage du scraping AIS")

    for vessel_name, url in vessels.items():
        logging.info(f"Scraping : {vessel_name}")
        try:
            data = get_vessel_data(url)

            if data is None:
                logging.warning(f"Aucune donnée récupérée pour {vessel_name}")
                continue

            df = pd.DataFrame([data])
            csv_file = os.path.join(data_folder, f"{vessel_name}.csv")

            if not os.path.exists(csv_file):
                df.to_csv(csv_file, index=False)
                logging.info(f"Fichier créé : {csv_file}")
            else:
                df.to_csv(csv_file, mode="a", header=False, index=False)
                logging.info(f"Données ajoutées au fichier : {csv_file}")

        except Exception as e:
            logging.error(f"Erreur pendant le scraping de {vessel_name}: {e}")

        time.sleep(5)  # pause pour éviter blocage du site

    logging.info("Scraping terminé")

if __name__ == "__main__":
    main()
'''import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re
import time

# ----- LISTE DES BATEAUX -----
vessels = {
    "CARITA": "https://www.vesselfinder.com/fr/vessels/details/9993042",
    "SY_TICONDEROGA": "https://www.vesselfinder.com/fr/vessels/details/367384280",
    "FORTUNATE_SUN": "https://www.vesselfinder.com/fr/vessels/details/1008243",
    "GULDEN_LEEUW": "https://www.vesselfinder.com/fr/vessels/details/5085897",
    "RISING_SUN": "https://www.vesselfinder.com/fr/vessels/details/8982307",
    "ARROW": "https://www.vesselfinder.com/fr/vessels/details/9970337",
    "PANTHALASSA": "https://www.vesselfinder.com/fr/vessels/details/9578103",
    "FRYDERYK_CHOPIN": "https://www.vesselfinder.com/fr/vessels/details/9030747"
}

data_folder = "data"

# créer dossier data si il n'existe pas
os.makedirs(data_folder, exist_ok=True)


# ----- EXTRACTION NOMBRE -----
def extract_number(text):
    if text is None:
        return None
    text = text.replace(",", ".")
    match = re.search(r"[-+]?\d*\.\d+|\d+", text)
    return float(match.group()) if match else None


# ----- SCRAPER DONNÉES -----
def get_vessel_data(url):

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Connection": "keep-alive"
}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Erreur connexion :", e)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    if "VesselFinder" not in response.text:
        print("Page bloquée ou incorrecte")
        return None

    data = {}

    ship_name = soup.find("h1")
    if ship_name:
        data["ship_name"] = ship_name.text.strip()

    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 2:
            key = cols[0].text.strip()
            value = cols[1].text.strip()
            data[key] = value

    data["timestamp"] = datetime.utcnow()

    position = data.get("Position", "")

    if "/" in position:
        parts = position.split("/")
        data["latitude"] = extract_number(parts[0])
        data["longitude"] = extract_number(parts[1])
    else:
        data["latitude"] = None
        data["longitude"] = None

    data["speed"] = extract_number(data.get("Speed"))
    data["course"] = extract_number(data.get("Course"))

    return data


# ----- SCRIPT PRINCIPAL -----
def main():

    print("Collecte des données AIS pour plusieurs bateaux")
    print("-" * 40)

    for vessel_name, url in vessels.items():

        print(f"Scraping : {vessel_name}")

        data = get_vessel_data(url)

        if data is None:
            print("Aucune donnée récupérée")
            continue

        df = pd.DataFrame([data])

        csv_file = os.path.join(data_folder, f"{vessel_name}.csv")

        if not os.path.exists(csv_file):
            df.to_csv(csv_file, index=False)
        else:
            df.to_csv(csv_file, mode="a", header=False, index=False)

        print(f"Données ajoutées dans {csv_file}")

        # pause pour éviter blocage du site
        time.sleep(5)

    print("Collecte terminée")


if __name__ == "__main__":
    main()
'''
