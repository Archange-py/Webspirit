# Webspirit

**Webspirit** est un gestionnaire de favoris qui tourne en local avec une extension pour le navigateur et une interface UI moderne pour une application de bureau.

## Prérequis

- Navigateur Chrome/Firefox/Edge

## Installation

1. Ouvrir un terminal à la racine du projet.

```bash
cd src/webspirit/application
```

2. Installer les dépendances Python :

```bash
pip install -r requirements.txt
```

## Lancement

1. **Démarrer l’application** :

```bash
python main.py
```

Le serveur FastAPI démarre en local sur `http://127.0.0.1:8000` et une icône apparaît dans la barre système. 

2. **Ouvrir l’interface web** :
- Cliquez sur l’icône système « BookmarksApp » et choisissez « Ouvrir
l’interface web ».
- Ou ouvrez `http://127.0.0.1:8000` dans votre navigateur.

3. **Charger l’extension navigateur** : 

- Dans Chrome/Edge, allez sur `chrome://extensions`, activez le mode
développeur, puis « Charger l’extension non empaquetée » et sélectionnez le
dossier `./extension/`.
- Dans Firefox, allez sur `about:debugging#/runtime/this-firefox`, cliquez
sur « Charger un module complémentaire temporaire » et choisissez
`manifest.json`.

4. **Tester la capture de favoris** : 

- Dans votre navigateur, chargez une page web. Cliquez sur l’icône de
l’extension ou utilisez le raccourci `Ctrl+Shift+Y`. L’URL et le titre sont
envoyés au serveur.
- Rafraîchissez la page de l’interface (`http://127.0.0.1:8000`) pour voir
le nouveau bookmark s’afficher.
