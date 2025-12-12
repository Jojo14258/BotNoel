"""
Module de configuration du bot Discord de Noël
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))

# Configuration du jeu
GIFT_LIFETIME = 5  # Durée d'apparition du cadeau en secondes
MIN_SPAWN_INTERVAL = 1  # Temps minimum entre deux cadeaux (5 minutes)
MAX_SPAWN_INTERVAL = 5  # Temps maximum entre deux cadeaux (30 minutes)
WIN_PROBABILITY = 0.25  # 15% de chance de gagner le rôle

# Émojis
GIFT_EMOJI = "🎁"
CHRISTMAS_TREE_EMOJI = "🎄"
SNOWFLAKE_EMOJI = "❄️"
STAR_EMOJI = "⭐"

# Nom du rôle à attribuer
CHRISTMAS_ROLE_NAME = "🎅 Elfe de Noël"

# Couleurs pour les embeds Discord
COLOR_SUCCESS = 0x00FF00  # Vert
COLOR_FAIL = 0xFF0000     # Rouge
COLOR_INFO = 0x3498db     # Bleu
COLOR_GIFT = 0xFFD700     # Or
