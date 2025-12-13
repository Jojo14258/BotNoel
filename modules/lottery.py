"""
Module de gestion du tirage au sort
"""

import discord
import random
import modules.config as config
from modules.config import (
    CHRISTMAS_ROLE_NAME,
    COLOR_SUCCESS,
    COLOR_FAIL,
    COLOR_INFO,
    STAR_EMOJI,
    SNOWFLAKE_EMOJI,
    LOG_CHANNEL_ID
)
from modules.fun_facts import get_random_fun_fact
from modules.books import BookManager, BOOK_TITLE, BOOK_EMOJI


class LotteryManager:
    """Gestionnaire du tirage au sort pour gagner le rôle"""
    
    def __init__(self, bot):
        self.bot = bot
        self.book_manager = BookManager()
        
    async def run_lottery(self, interaction: discord.Interaction, user: discord.Member):
        """
        Lance le tirage au sort pour un utilisateur
        
        Args:
            interaction: L'interaction Discord
            user: L'utilisateur qui a récupéré le cadeau
        """
        # Vérifier si l'utilisateur a déjà tout gagné (rôle ET livre)
        role = await self.get_or_create_role(interaction.guild)
        has_role = role in user.roles
        has_book = self.book_manager.has_won_book(user)
        
        if has_role and has_book:
            # L'utilisateur a tout gagné, il ne peut plus jouer
            embed = discord.Embed(
                title=f"{STAR_EMOJI} Vous avez tout gagné !",
                description=f"{user.mention}, vous avez déjà le rôle **{CHRISTMAS_ROLE_NAME}** ET le livre **{BOOK_TITLE}** ! 🎉\n\n"
                           f"Laissez les autres jouer ! 🎄",
                color=COLOR_INFO
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Tirage pour le livre (prioritaire et très rare !)
        if not has_book:
            # Vérifier le stock de livres
            if config.MAX_BOOKS != -1 and config.BOOKS_GIVEN >= config.MAX_BOOKS:
                # Plus de livres disponibles
                pass
            else:
                won_book = random.random() < config.BOOK_PROBABILITY
                
                if won_book:
                    # L'utilisateur gagne le livre !
                    self.book_manager.add_winner(user)
                    config.BOOKS_GIVEN += 1
                    
                    embed = self.book_manager.create_win_embed(user)
                    await interaction.response.send_message(embed=embed)
                    
                    # Logger le gain
                    await self.log_win(interaction.guild, user, "book")
                    return
        
        # Tirage pour le rôle
        if not has_role:
            # Vérifier le stock de rôles
            if config.MAX_ROLES != -1 and config.ROLES_GIVEN >= config.MAX_ROLES:
                # Plus de rôles disponibles
                pass
            else:
                has_won_role = random.random() < config.ROLE_PROBABILITY
                
                if has_won_role:
                    # L'utilisateur gagne le rôle !
                    try:
                        await user.add_roles(role)
                        config.ROLES_GIVEN += 1
                        
                        embed = discord.Embed(
                            title=f"{STAR_EMOJI} FÉLICITATIONS ! {STAR_EMOJI}",
                            description=f"🎊 {user.mention} a gagné le rôle **{CHRISTMAS_ROLE_NAME}** ! 🎊\n\n"
                                       f"Bienvenue dans l'équipe des lutins du Père Noël ! 🎅",
                            color=COLOR_SUCCESS
                        )
                        embed.set_thumbnail(url=user.display_avatar.url)
                        
                        await interaction.response.send_message(embed=embed)
                        
                        # Logger le gain
                        await self.log_win(interaction.guild, user, "role")
                        
                    except discord.Forbidden:
                        # Erreur de permissions
                        embed = discord.Embed(
                            title="❌ Erreur de permissions",
                            description=f"Vous avez gagné, mais je ne peux pas vous attribuer le rôle !\n\n"
                                       f"**Raisons possibles :**\n"
                                       f"• Mon rôle doit être au-dessus du rôle '{CHRISTMAS_ROLE_NAME}' dans la hiérarchie\n"
                                       f"• Je dois avoir la permission 'Gérer les rôles'\n\n"
                                       f"Contactez un administrateur !",
                            color=COLOR_FAIL
                        )
                        await interaction.response.send_message(embed=embed)
                    except Exception as e:
                        # Autre erreur
                        embed = discord.Embed(
                            title="❌ Erreur inattendue",
                            description=f"Une erreur est survenue : {str(e)}",
                            color=COLOR_FAIL
                        )
                        await interaction.response.send_message(embed=embed)
                    return
        
        # L'utilisateur ne gagne rien, on lui donne un fun fact
        fun_fact = get_random_fun_fact()
        
        embed = discord.Embed(
            title=f"{SNOWFLAKE_EMOJI} Pas de chance cette fois !",
            description=f"{user.mention}, vous n'avez rien gagné... mais voici un fun fact sur Noël ! 🎄\n\n"
                       f"**{fun_fact}**",
            color=COLOR_FAIL
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def log_win(self, guild: discord.Guild, user: discord.Member, win_type: str):
        """
        Log un gain dans le canal de logs
        
        Args:
            guild: Le serveur Discord
            user: L'utilisateur qui a gagné
            win_type: Type de gain ("role" ou "book")
        """
        if LOG_CHANNEL_ID == 0:
            return  # Pas de canal de logs configuré
        
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel is None:
            return
        
        if win_type == "book":
            books_remaining = config.MAX_BOOKS - config.BOOKS_GIVEN if config.MAX_BOOKS != -1 else "∞"
            
            embed = discord.Embed(
                title=f"{BOOK_EMOJI} Livre gagné !",
                description=f"{user.mention} ({user.name}) a gagné **{BOOK_TITLE}** !",
                color=COLOR_SUCCESS,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(
                name="📊 Stock restant",
                value=f"📚 Livres: **{books_remaining}**",
                inline=False
            )
        elif win_type == "role":
            roles_remaining = config.MAX_ROLES - config.ROLES_GIVEN if config.MAX_ROLES != -1 else "∞"
            
            embed = discord.Embed(
                title=f"🎅 Rôle gagné !",
                description=f"{user.mention} ({user.name}) a gagné le rôle **{CHRISTMAS_ROLE_NAME}** !",
                color=COLOR_INFO,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(
                name="📊 Stock restant",
                value=f"🎅 Rôles: **{roles_remaining}**",
                inline=False
            )
        else:
            return
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass  # Ignorer les erreurs de log
            
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
