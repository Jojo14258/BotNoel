"""
Module de gestion des cadeaux
"""

import discord
import asyncio
import random
from datetime import datetime
import modules.config as config
from modules.config import (
    GIFT_EMOJI,
    CHRISTMAS_TREE_EMOJI,
    COLOR_GIFT
)


class GiftManager:
    """Gestionnaire des apparitions de cadeaux"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_gift = None
        self.is_running = False
        self.claimed_by = None
        
    async def spawn_gift(self, channel):
        """Fait apparaître un cadeau dans le canal"""
        # Créer l'embed du cadeau
        embed = discord.Embed(
            title=f"{GIFT_EMOJI} Un cadeau sauvage apparaît ! {GIFT_EMOJI}",
            description=f"{CHRISTMAS_TREE_EMOJI} Soyez rapide ! Cliquez sur le bouton pour tenter votre chance !",
            color=COLOR_GIFT,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Ce cadeau disparaîtra dans {config.GIFT_LIFETIME} secondes...")
        
        # Créer le bouton
        view = GiftView(self)
        
        # Envoyer le message
        self.active_gift = await channel.send(embed=embed, view=view)
        self.claimed_by = None
        
        # Attendre la durée de vie du cadeau
        await asyncio.sleep(config.GIFT_LIFETIME)
        
        # Si personne n'a récupéré le cadeau, le supprimer
        if self.claimed_by is None and self.active_gift:
            try:
                await self.active_gift.delete()
            except discord.NotFound:
                pass
            self.active_gift = None
            
    async def claim_gift(self, interaction: discord.Interaction):
        """Gère la réclamation d'un cadeau"""
        # Vérifier si quelqu'un a déjà réclamé ce cadeau
        if self.claimed_by is not None:
            await interaction.response.send_message(
                f"Trop tard ! {self.claimed_by.mention} a déjà récupéré ce cadeau !",
                ephemeral=True
            )
            return None
            
        # Marquer le cadeau comme réclamé
        self.claimed_by = interaction.user
        
        # Supprimer le message du cadeau
        if self.active_gift:
            try:
                await self.active_gift.delete()
            except discord.NotFound:
                pass
            self.active_gift = None
            
        return interaction.user
        
    async def start_spawn_loop(self, channel):
        """Lance la boucle d'apparition des cadeaux"""
        self.is_running = True
        
        while self.is_running:
            # Attendre un délai aléatoire
            wait_time = random.randint(config.MIN_SPAWN_INTERVAL, config.MAX_SPAWN_INTERVAL)
            await asyncio.sleep(wait_time)
            
            # Faire apparaître un cadeau
            if self.is_running:
                await self.spawn_gift(channel)
                
    def stop_spawn_loop(self):
        """Arrête la boucle d'apparition des cadeaux"""
        self.is_running = False


class GiftView(discord.ui.View):
    """Vue contenant le bouton pour récupérer le cadeau"""
    
    def __init__(self, gift_manager: GiftManager):
        super().__init__(timeout=config.GIFT_LIFETIME)
        self.gift_manager = gift_manager
        
    @discord.ui.button(label="Récupérer le cadeau !", style=discord.ButtonStyle.success, emoji=GIFT_EMOJI)
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour récupérer le cadeau"""
        # Importer ici pour éviter les imports circulaires
        from modules.lottery import LotteryManager
        
        user = await self.gift_manager.claim_gift(interaction)
        
        if user:
            # Lancer le tirage au sort
            lottery = LotteryManager(self.gift_manager.bot)
            await lottery.run_lottery(interaction, user)
            
            # Désactiver le bouton
            button.disabled = True
            self.stop()
