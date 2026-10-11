import os
import sys
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
# GitHub Actions passe une chaîne vide si le secret n'existe pas : `or` garde la valeur par défaut
INLI_SEARCH_URL = os.getenv('INLI_SEARCH_URL') or 'https://www.inli.fr/locations/offres/paris-departement_d:75'

SEEN_FILE = 'seen_ids.json'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erreur Telegram : {e}")
        return False

def load_seen_ids():
    """Charger les IDs des annonces déjà vues"""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def save_seen_ids(seen_ids):
    """Sauvegarder les IDs des annonces vues"""
    with open(SEEN_FILE, 'w') as f:
        json.dump(sorted(seen_ids), f, indent=2)

def parse_annonces(html):
    """
    Extraire les annonces depuis le HTML de la page In'li.
    Chaque annonce est un div.featured-item contenant :
    - Un lien <a href="/location-appartement-ville-XXXXX/PRV-XXXXXX">
    - Le texte avec le prix, la surface, le nombre de pièces, la ville
    """
    soup = BeautifulSoup(html, 'html.parser')
    annonces = []

    for item in soup.select('.featured-item'):
        link_tag = item.find('a')
        if not link_tag:
            continue

        href = link_tag.get('href', '')
        # Extraire l'ID unique depuis l'URL (ex: PRV-386083)
        match = re.search(r'/([\w]+-\d+)$', href)
        if not match:
            continue

        annonce_id = match.group(1)
        texte = item.get_text(separator=' | ', strip=True)

        # Essayer d'extraire les détails depuis le texte
        prix_match = re.search(r'([\d\s]+)\s*€', texte.replace('\xa0', ' '))
        surface_match = re.search(r'([\d.,]+)\s*m²', texte)
        pieces_match = re.search(r'(\d+)\s*pièces?', texte)
        # La ville est généralement le dernier élément du texte
        ville = texte.split('|')[-1].strip() if '|' in texte else ''

        annonces.append({
            'id': annonce_id,
            'url': f"https://www.inli.fr{href}",
            'prix': prix_match.group(1).strip() if prix_match else 'N/A',
            'surface': surface_match.group(1) if surface_match else 'N/A',
            'pieces': pieces_match.group(1) if pieces_match else 'N/A',
            'ville': ville,
            'neuf': 'Neuf' in texte,
        })

    return annonces

def main():
    print(f"[{datetime.now()}] Vérification de la page In'li...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(INLI_SEARCH_URL, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur HTTP : {e}")
        sys.exit(1)

    # Vérifier s'il y a des annonces sur la page
    if "Aucune annonce disponible" in response.text:
        print("Aucune annonce disponible pour le moment.")
        return

    # Parser les annonces
    annonces = parse_annonces(response.text)
    print(f"{len(annonces)} annonce(s) trouvée(s) sur la page.")

    if not annonces:
        print("Page modifiée mais aucune annonce parseable.")
        sys.exit(1)

    # Charger les annonces déjà vues
    seen_ids = load_seen_ids()
    nouvelles = [a for a in annonces if a['id'] not in seen_ids]

    if not nouvelles:
        print("Toutes les annonces ont déjà été notifiées.")
        return

    print(f"{len(nouvelles)} nouvelle(s) annonce(s) détectée(s) !")

    echecs = 0
    for annonce in nouvelles:
        neuf_tag = "🏗️ Neuf | " if annonce['neuf'] else ""
        message = (
            f"🚨 <b>Nouvelle Annonce Inli !</b> 🚨\n\n"
            f"📍 <b>Ville :</b> {annonce['ville']}\n"
            f"📏 <b>Surface :</b> {annonce['surface']} m² ({annonce['pieces']} pièces)\n"
            f"💶 <b>Loyer :</b> {annonce['prix']} € CC\n"
            f"{neuf_tag}\n"
            f"🔗 <a href=\"{annonce['url']}\">Voir l'annonce</a>"
        )
        if not send_telegram_message(message):
            echecs += 1
            continue
        seen_ids.add(annonce['id'])
        print(f"  -> Notification envoyee : {annonce['id']} ({annonce['ville']})")

    save_seen_ids(seen_ids)
    print("IDs sauvegardés.")

    if echecs:
        print(f"{echecs} notification(s) non envoyée(s), nouvel essai au prochain passage.")
        sys.exit(1)

if __name__ == "__main__":
    main()
