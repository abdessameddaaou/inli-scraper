# Inli Scraper Bot 🏠🔔

Bot automatique qui surveille les annonces sur [inli.fr](https://www.inli.fr) et envoie une notification Telegram dès qu'un nouveau logement apparaît.

## Fonctionnement

- Toutes les **5 minutes**, du **lundi au vendredi**, de **8h à 21h** (heure de Paris)
- Le week-end et hors horaires, le workflow s'arrête immédiatement (job `check`), même s'il est déclenché par un appel externe (`repository_dispatch`)
- Un lancement manuel (**Run workflow**) s'exécute toujours, quel que soit le jour
- Le script charge la page de recherche In'li
- Il compare les annonces avec celles déjà vues (`seen_ids.json`)
- S'il y a une **nouvelle annonce**, il envoie un message Telegram avec les détails et le lien

## Configuration

### 1. Créer un Bot Telegram
1. Ouvrez Telegram et cherchez **@BotFather**
2. Envoyez `/newbot` et suivez les instructions
3. Copiez le **Token** fourni

### 2. Trouver votre Chat ID
1. Cherchez **@userinfobot** sur Telegram
2. Cliquez sur Démarrer
3. Copiez votre **Id**

### 3. Ajouter les Secrets GitHub
Allez dans **Settings > Secrets and variables > Actions** de votre dépôt et ajoutez :

| Secret | Valeur |
|--------|--------|
| `TELEGRAM_BOT_TOKEN` | Le token de BotFather |
| `TELEGRAM_CHAT_ID` | Votre Chat ID |
| `INLI_SEARCH_URL` | *(optionnel)* URL de recherche In'li — par défaut Paris (75) |

### Tester la notification en local
```bash
TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=yyy python test_notif.py
```

### 4. Activer GitHub Actions
Le workflow se lance automatiquement selon le planning. Vous pouvez aussi le lancer manuellement depuis l'onglet **Actions** > **Run workflow**.
