import requests

TOKEN = '8707801230:AAG0srIN94csOcJsZ6FT8EaIuQeCyrUkN0g'
CHAT_ID = '5738132883'

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
    json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
)
print(r.status_code, r.json())
