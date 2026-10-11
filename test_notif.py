"""Envoie une notification de test sur Telegram.

Usage :
    TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=yyy python test_notif.py
"""
import os
import sys

import requests

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TOKEN or not CHAT_ID:
    sys.exit("Définis TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID avant de lancer le test.")

message = (
    "🚨 <b>Nouvelle Annonce Inli !</b> 🚨\n\n"
    "📍 <b>Ville :</b> Paris 15e\n"
    "📏 <b>Surface :</b> 45.5 m² (2 pièces)\n"
    "💶 <b>Loyer :</b> 890 € CC\n"
    "🏗️ Neuf\n\n"
    "🔗 <a href='https://www.inli.fr/locations/offres/paris-departement_d:75'>Voir l'annonce</a>"
)

r = requests.post(
    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
    json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'},
    timeout=30,
)
print(r.status_code, r.json())
