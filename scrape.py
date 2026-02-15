import requests
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

URL = "https://pc-api.polestar.com/eu-north-1/partner-rm-tool/public/"

payload = {
    "operationName": "SearchVehicleAds",
    "variables": {
        "carModel": "PS2",
        "market": "gb",
        "offset": 0,
        "limit": 100,
        "sortOrder": "Ascending",
        "sortProperty": "Price",
        "equalFilters": [],
        "excludeFilters": [{"filterType": "CycleState", "value": "New"}]
    },
    "query": """
    query SearchVehicleAds($carModel: CarModel!, $market: String!, $offset: Int!, $limit: Int!, $sortOrder: SortOrder2!, $sortProperty: SortProperty!, $equalFilters: [EqualFilter!], $excludeFilters: [ExcludeFilter!]) {
      searchVehicleAds(
        carModel: $carModel
        market: $market
        offset: $offset
        limit: $limit
        sortOrder: $sortOrder
        sortProperty: $sortProperty
        equalFilters: $equalFilters
        excludeFilters: $excludeFilters
      ) {
        ads {
          id
          registrationDate
          mileage
          price {
            amount
          }
        }
      }
    }
    """
}

response = requests.post(URL, json=payload)
data = response.json()

print("Full response:")
print(data)

ads = data["data"]["searchVehicleAds"]["ads"]

cars = []

for car in ads:
    reg_year = int(car["registrationDate"][:4])
    mileage = car["mileage"]
    price = car["price"]["amount"]

    if reg_year >= 2023 and mileage <= 45000:
        cars.append({
            "id": car["id"],
            "registration_year": reg_year,
            "mileage": mileage,
            "price": price,
            "scraped_at": datetime.utcnow().isoformat()
        })

df = pd.DataFrame(cars)

print("Cars matching filters:", len(df))

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
client = gspread.authorize(creds)

sheet = client.open_by_key("1PlCdbnvpW-f4iSAgDAioF7nvP1KV7eEH2VMHvL87FOU").sheet1
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())
