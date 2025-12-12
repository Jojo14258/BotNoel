# 🎄 Bot Discord de Noël - Jeu de Cadeaux

Un bot Discord interactif qui fait apparaître des cadeaux aléatoirement dans un canal. Les utilisateurs peuvent les récupérer pour tenter de gagner un rôle spécial de Noël !

## 🎁 Fonctionnalités

- **Apparition aléatoire de cadeaux** : Les cadeaux apparaissent à des intervalles aléatoires (5-30 minutes par défaut)
- **Durée limitée** : Chaque cadeau ne reste visible que 5 secondes
- **Bouton interactif** : Seul le premier utilisateur à cliquer peut récupérer le cadeau
- **Système de tirage au sort** : 15% de chance de gagner le rôle "🎅 Elfe de Noël"
- **Fun facts** : Si l'utilisateur ne gagne pas, il reçoit un fait amusant sur Noël
- **Code modulaire** : Architecture claire et maintenable

## 📁 Structure du projet

```
botNoel/
├── bot.py                      # Point d'entrée principal
├── modules/
│   ├── __init__.py
│   ├── config.py              # Configuration et constantes
│   ├── gift_manager.py        # Gestion de l'apparition des cadeaux
│   ├── lottery.py             # Gestion du tirage au sort
│   └── fun_facts.py           # Base de données des fun facts
├── data/                      # Dossier pour les données (optionnel)
├── requirements.txt           # Dépendances Python
├── .env.example              # Exemple de configuration
├── .gitignore
└── README.md
```

## 🚀 Installation

### 1. Prérequis

- Python 3.8 ou supérieur
- Un compte Discord
- Un serveur Discord où vous avez les permissions d'administrateur

### 2. Créer une application Discord

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Cliquez sur "New Application"
3. Donnez un nom à votre application (ex: "Bot de Noël")
4. Allez dans l'onglet "Bot"
5. Cliquez sur "Add Bot"
6. Activez les "Privileged Gateway Intents" suivants :
   - `PRESENCE INTENT`
   - `SERVER MEMBERS INTENT`
   - `MESSAGE CONTENT INTENT`
7. Copiez le token du bot (vous en aurez besoin plus tard)

### 3. Inviter le bot sur votre serveur

1. Dans le Developer Portal, allez dans l'onglet "OAuth2" > "URL Generator"
2. Sélectionnez les scopes :
   - `bot`
   - `applications.commands`
3. Sélectionnez les permissions :
   - `Send Messages`
   - `Embed Links`
   - `Read Message History`
   - `Use Slash Commands`
   - `Manage Roles`
4. Copiez l'URL générée et ouvrez-la dans votre navigateur
5. Sélectionnez votre serveur et autorisez le bot

### 4. Configuration du projet

1. Clonez ou téléchargez ce projet
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet (copie de `.env.example`) :
```env
DISCORD_TOKEN=votre_token_ici
CHANNEL_ID=0
```

Remplacez `votre_token_ici` par le token de votre bot Discord.

> **Note** : Si `CHANNEL_ID=0`, les cadeaux apparaîtront dans le canal où vous lancez la commande `!start`. Sinon, mettez l'ID du canal souhaité.

### 5. Personnalisation (optionnel)

Vous pouvez modifier les paramètres du jeu dans `modules/config.py` :

```python
GIFT_LIFETIME = 5           # Durée d'apparition du cadeau (secondes)
MIN_SPAWN_INTERVAL = 300    # Intervalle minimum entre cadeaux (secondes)
MAX_SPAWN_INTERVAL = 1800   # Intervalle maximum entre cadeaux (secondes)
WIN_PROBABILITY = 0.15      # Probabilité de gagner (15%)
CHRISTMAS_ROLE_NAME = "🎅 Elfe de Noël"  # Nom du rôle à attribuer
```

## 🎮 Utilisation

### Démarrer le bot

```bash
python bot.py
```

### Commandes disponibles

#### Pour tous les utilisateurs :

- `!info` - Affiche les informations sur le jeu
- `!help` - Affiche la liste des commandes

#### Pour les administrateurs uniquement :

- `!start` - Démarre le jeu de cadeaux
- `!stop` - Arrête le jeu de cadeaux

### Comment jouer

1. Un administrateur lance `!start` dans un canal
2. Des cadeaux apparaîtront aléatoirement
3. Soyez le premier à cliquer sur le bouton "Récupérer le cadeau !"
4. Vous avez une chance de gagner le rôle spécial ou de découvrir un fun fact

## 🔧 Modules

### `config.py`
Contient toutes les constantes et paramètres de configuration du bot.

### `gift_manager.py`
Gère l'apparition et la disparition des cadeaux :
- Classe `GiftManager` : Contrôle la boucle d'apparition
- Classe `GiftView` : Gère le bouton interactif

### `lottery.py`
Gère le système de tirage au sort :
- Attribution du rôle en cas de victoire
- Création automatique du rôle s'il n'existe pas
- Vérification que l'utilisateur n'a pas déjà le rôle

### `fun_facts.py`
Base de données de 30+ fun facts sur Noël et les fêtes de fin d'année.

### `bot.py`
Point d'entrée principal avec :
- Initialisation du bot
- Commandes Discord
- Gestion des erreurs

## 🎨 Personnalisation des fun facts

Pour ajouter vos propres fun facts, éditez le fichier `modules/fun_facts.py` :

```python
FUN_FACTS = [
    "Votre fun fact ici...",
    "Un autre fun fact...",
    # Ajoutez autant de fun facts que vous voulez !
]
```

## 🐛 Dépannage

### Le bot ne se connecte pas
- Vérifiez que votre token dans le fichier `.env` est correct
- Assurez-vous d'avoir activé les intents dans le Developer Portal

### Les boutons ne fonctionnent pas
- Vérifiez que vous utilisez `discord.py` version 2.0 ou supérieure
- Assurez-vous que le bot a les permissions nécessaires

### Le rôle n'est pas attribué
- Vérifiez que le bot a la permission "Manage Roles"
- Assurez-vous que le rôle du bot est au-dessus du rôle à attribuer dans la hiérarchie

## 📝 Licence

Ce projet est libre d'utilisation pour un usage personnel ou communautaire.

## 🎅 Joyeux Noël !

Amusez-vous bien avec votre bot de Noël ! 🎄❄️
