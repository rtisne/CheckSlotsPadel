import os
import sys
import requests
from datetime import date, datetime, timedelta

# → 1️⃣ Calcul de la date cible : jeudi, deux semaines après aujourd’hui
today = date.today()
two_weeks = today + timedelta(weeks=2)
# Jeudi = weekday() == 3 (lundi=0)
days_until_thursday = (3 - two_weeks.weekday()) % 7
target_date = two_weeks + timedelta(days=days_until_thursday)
date_to_check = target_date.isoformat()

# → 2️⃣ Heure fixe à vérifier
hours_to_check = ["12:30"]
from_time = hours_to_check[0]
to_time = (datetime.strptime(hours_to_check[-1], "%H:%M") + timedelta(hours=1)).strftime("%H:%M:%S")

API_URL = (
    f"https://api-v3.doinsport.club/clubs/playgrounds/plannings/{date_to_check}"
    f"?club.id=adc3cc48-4163-4fe5-91fe-72ba71a400ee&from={from_time}&to={to_time}"
    f"&activities.id=ce8c306e-224a-4f24-aa9d-6500580924dc&bookingType=unique"
)
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

def send_pushover_notification(slot_time):
    message = f"✅ Créneau dispo le {date_to_check} à {slot_time}."
    payload = {"token": PUSHOVER_API_TOKEN, "user": PUSHOVER_USER_KEY, "message": message}
    try:
        r = requests.post(PUSHOVER_URL, data=payload)
        r.raise_for_status()
        print(f"[OK] Notification envoyée pour {date_to_check} {slot_time}")
    except Exception as e:
        print(f"[ERR] Échec notification : {e}")

def check_slots():
    try:
        resp = requests.get(API_URL)
        resp.raise_for_status()
        for member in resp.json().get("hydra:member", []):
            if "Single" in member.get("name", ""):
                continue
            for activity in member.get("activities", []):
                for slot in activity.get("slots", []):
                    if slot.get("startAt") in hours_to_check and any(p.get("bookable") for p in slot.get("prices", [])):
                        send_pushover_notification(slot["startAt"])
                        return
        print(f"[INFO] Aucun créneau le {date_to_check} à {from_time}")
    except Exception as e:
        print(f"[ERR] Requête API : {e}")

if __name__ == "__main__":
    print(f"▶️ Recherche du créneau {date_to_check} à {from_time}")
    check_slots()
