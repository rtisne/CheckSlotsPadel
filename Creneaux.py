import requests
import os
import sys

# Récupérer la date à vérifier en tant qu'argument
date_to_check = sys.argv[1] if len(sys.argv) > 1 else "2024-11-14"

# URL de l'API avec la date dynamique
API_URL = f"https://api-v3.doinsport.club/clubs/playgrounds/plannings/{date_to_check}?club.id=adc3cc48-4163-4fe5-91fe-72ba71a400ee&from=12:00:00&to=14:00:00&activities.id=ce8c306e-224a-4f24-aa9d-6500580924dc&bookingType=unique"
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

def check_slots():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        
        # Rechercher les créneaux bookables pour les horaires spécifiés
        for member in data.get("hydra:member", []):
            playground_name = member.get("name", "")
            if "Single" in playground_name:
                continue  # Ignorer ce terrain et passer au suivant
                
            for activity in member.get("activities", []):
                for slot in activity.get("slots", []):
                    start_time = slot.get("startAt")
                    is_bookable = any(price.get("bookable") for price in slot.get("prices", []))
                    
                    if start_time in ["12:15", "12h30", "12:45"] and is_bookable:
                        send_pushover_notification(start_time, date_to_check)
                        return
        print("pas de créneaux pour " + date_to_check)
    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")

def send_pushover_notification(slot_time, date):
    message = f"Un créneau est disponible le {date} à {slot_time}."
    payload = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message
    }
    try:
        response = requests.post(PUSHOVER_URL, data=payload)
        response.raise_for_status()
        print(f"Notification envoyée pour le créneau le {date} à {slot_time}.")
    except requests.RequestException as e:
        print(f"Erreur lors de l'envoi de la notification : {e}")

# Exécution du script
if __name__ == "__main__":
    check_slots()
