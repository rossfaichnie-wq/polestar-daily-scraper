import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

URL = "https://www.polestar.com/uk/preowned-cars/search/"

html = requests.get(URL, timeout=30).text
soup = BeautifulSoup(html, "html.parser")

cars = []

for card in soup.select("a[href*='/preowned-cars/product/']"):
    text = card.get_text(" ", strip=True)
    if "Polestar 2" in text:
        cars.append({
            "raw_text": text,
            "scraped_at": datetime.utcnow().isoformat()
        })

df = pd.DataFrame(cars)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
client = gspread.authorize(creds)

sheet = client.open_by_key("1PlCdbnvpW-f4iSAgDAioF7nvP1KV7eEH2VMHvL87FOU").sheet1
sheet.update([df.columns.values.tolist()] + df.values.tolist())
