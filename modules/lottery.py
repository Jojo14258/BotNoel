"""
Module de gestion du tirage au sort
"""

import discord
import random
from modules.config import (
    WIN_PROBABILITY,
    CHRISTMAS_ROLE_NAME,
    COLOR_SUCCESS,
    COLOR_FAIL,
    STAR_EMOJI,
    SNOWFLAKE_EMOJI
)
from modules.fun_facts import get_random_fun_fact


class LotteryManager:
    """Gestionnaire du tirage au sort pour gagner le rôle"""
    
    def __init__(self, bot):
        self.bot = bot
        
    async def run_lottery(self, interaction: discord.Interaction, user: discord.Member):
        """
        Lance le tirage au sort pour un utilisateur
        
        Args:
            interaction: L'interaction Discord
            user: L'utilisateur qui a récupéré le cadeau
        """
        # Vérifier si l'utilisateur a déjà le rôle
        role = await self.get_or_create_role(interaction.guild)
        
        if role in user.roles:
            # L'utilisateur a déjà le rôle
            embed = discord.Embed(
                title=f"{SNOWFLAKE_EMOJI} Déjà élue !",
                description=f"{user.mention}, vous avez déjà le rôle **{CHRISTMAS_ROLE_NAME}** ! Laissez les autres jouer ! 🎄",
                color=COLOR_FAIL
            )
            await interaction.response.send_message(embed=embed)
            return
            
        # Effectuer le tirage
        has_won = random.random() < WIN_PROBABILITY
        
        if has_won:
            # L'utilisateur gagne le rôle !
            await user.add_roles(role)
            
            embed = discord.Embed(
                title=f"{STAR_EMOJI} FÉLICITATIONS ! {STAR_EMOJI}",
                description=f"🎊 {user.mention} a gagné le rôle **{CHRISTMAS_ROLE_NAME}** ! 🎊\n\n"
                           f"Bienvenue dans l'équipe des lutins du Père Noël ! 🎅",
                color=COLOR_SUCCESS
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
        else:
            # L'utilisateur ne gagne pas, on lui donne un fun fact
            fun_fact = get_random_fun_fact()
            
            embed = discord.Embed(
                title=f"{SNOWFLAKE_EMOJI} Pas de chance cette fois !",
                description=f"{user.mention}, vous n'avez pas gagné le rôle... mais voici un fun fact sur Noël ! 🎄\n\n"
                           f"**{fun_fact}**",
                color=COLOR_FAIL
            )
            
            await interaction.response.send_message(embed=embed)
            
    async def get_or_create_role(self, guild: discord.Guild) -> discord.Role:
        """
        Récupère ou crée le rôle de Noël
        
        Args:
            guild: Le serveur Discord
            
        Returns:
            Le rôle de Noël
        """
        # Chercher si le rôle existe déjà
        role = discord.utils.get(guild.roles, name=CHRISTMAS_ROLE_NAME)
        
        if role is None:
            # Créer le rôle s'il n'existe pas
            role = await guild.create_role(
                name=CHRISTMAS_ROLE_NAME,
                color=discord.Color.red(),
                hoist=True,  # Afficher séparément dans la liste des membres
                mentionable=True
            )
            
        return role
