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
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', 0))  # Canal pour les logs des gains

# Configuration du jeu
GIFT_LIFETIME = 5  # Durée d'apparition du cadeau en secondes
MIN_SPAWN_INTERVAL = 1  # Temps minimum entre deux cadeaux (5 minutes)
MAX_SPAWN_INTERVAL = 5  # Temps maximum entre deux cadeaux (30 minutes)
ROLE_PROBABILITY = 0.25  # Probabilité de gagner le rôle
BOOK_PROBABILITY = 0.05  # 5% de chance de gagner le livre (très rare !)

# Stock de récompenses
MAX_ROLES = 10  # Nombre maximum de rôles à distribuer (-1 = illimité)
MAX_BOOKS = 3   # Nombre maximum de livres à distribuer (-1 = illimité)
ROLES_GIVEN = 0  # Nombre de rôles déjà distribués
BOOKS_GIVEN = 0  # Nombre de livres déjà distribués

# Émojis
GIFT_EMOJI = "🎁"
CHRISTMAS_TREE_EMOJI = "🎄"
SNOWFLAKE_EMOJI = "❄️"
STAR_EMOJI = "⭐"

# Nom du rôle à attribuer
CHRISTMAS_ROLE_NAME = "🎅 Elfe de Noël 2025"

# Couleurs pour les embeds Discord
COLOR_SUCCESS = 0x00FF00  # Vert
COLOR_FAIL = 0xFF0000     # Rouge
COLOR_INFO = 0x3498db     # Bleu
COLOR_GIFT = 0xFFD700     # Or
