"""
Module de gestion des livres à gagner
"""

import discord
import json
import os
from modules.config import COLOR_SUCCESS, STAR_EMOJI

# Livre disponible
BOOK_TITLE = "Guide de survie au lycée"
BOOK_EMOJI = "📚"

# Chemin du fichier de sauvegarde
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
WINNERS_FILE = os.path.join(DATA_DIR, "book_winners.json")


class BookManager:
    """Gestionnaire des livres gagnés"""
    
    def __init__(self):
        self.winners = []  # Liste des IDs des gagnants de livres
        self._load_winners()
        
    def _load_winners(self):
        """Charge la liste des gagnants depuis le fichier"""
        try:
            if os.path.exists(WINNERS_FILE):
                with open(WINNERS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.winners = data.get('winners', [])
        except Exception as e:
            print(f"Erreur lors du chargement des gagnants du livre : {e}")
            self.winners = []
    
    def _save_winners(self):
        """Sauvegarde la liste des gagnants dans le fichier"""
        try:
            # Créer le dossier data s'il n'existe pas
            os.makedirs(DATA_DIR, exist_ok=True)
            
            with open(WINNERS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'winners': self.winners}, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des gagnants du livre : {e}")
        
    def add_winner(self, user: discord.Member):
        """Ajoute un gagnant à la liste"""
        if user.id not in self.winners:
            self.winners.append(user.id)
            self._save_winners()
            return True
        return False
    
    def has_won_book(self, user: discord.Member) -> bool:
        """Vérifie si l'utilisateur a déjà gagné le livre"""
        return user.id in self.winners
    
    def create_win_embed(self, user: discord.Member) -> discord.Embed:
        """Crée l'embed pour annoncer un gain de livre"""
        embed = discord.Embed(
            title=f"{STAR_EMOJI} INCROYABLE ! {STAR_EMOJI}",
            description=f"{BOOK_EMOJI} {user.mention} a gagné le livre **'{BOOK_TITLE}'** ! {BOOK_EMOJI}\n\n"
                       f"Félicitations pour cette chance exceptionnelle ! 🎉",
            color=COLOR_SUCCESS
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Livre gagné : {BOOK_TITLE}")
        return embed
