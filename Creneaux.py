import requests
import os
import sys
from datetime import datetime, timedelta

date_to_check = sys.argv[1] if len(sys.argv) > 1 else "2024-11-14"
hours_to_check = (sys.argv[2] if len(sys.argv) > 1 else "12:15,12:30,12:45").split(",")

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
    """Envoie une notification via Pushover."""
    message = f"Un créneau est disponible le {date_to_check} à {slot_time}."
    payload = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message,
    }
    try:
        response = requests.post(PUSHOVER_URL, data=payload)
        response.raise_for_status()
        print(f"Notification envoyée pour le créneau {slot_time}.")
    except requests.RequestException as e:
        print(f"Erreur lors de l'envoi de la notification : {e}")

def check_slots():
    """Vérifie les créneaux disponibles."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        slots = response.json().get("hydra:member", [])

        for member in slots:
            if "Single" in member.get("name", ""):
                continue

            for activity in member.get("activities", []):
                for slot in activity.get("slots", []):
                    if slot.get("startAt") in hours_to_check and any(price.get("bookable") for price in slot.get("prices", [])):
                        send_pushover_notification(slot["startAt"])
                        return

        print(f"Aucun créneau disponible pour {date_to_check}.")
    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")

if __name__ == "__main__":
    check_slots()
