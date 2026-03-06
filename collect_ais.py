import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import re
import time

# ----- LISTE DES BATEAUX -----
vessels = {
    "CARITA": "https://www.vesselfinder.com/fr/vessels/details/9993042",
    "SY TICONDEROGA": "https://www.vesselfinder.com/fr/vessels/details/367384280",
    "FORTUNATE SUN": "https://www.vesselfinder.com/fr/vessels/details/1008243",
    "GULDEN LEEUW": "https://www.vesselfinder.com/fr/vessels/details/5085897",
    "RISING SUN": "https://www.vesselfinder.com/fr/vessels/details/8982307",
    "ARROW": "https://www.vesselfinder.com/fr/vessels/details/9970337",
    "PANTHALASSA": "https://www.vesselfinder.com/fr/vessels/details/9578103",
    "FRYDERYK CHOPIN": "https://www.vesselfinder.com/fr/vessels/details/9030747"
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
